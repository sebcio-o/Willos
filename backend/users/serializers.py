import pyotp
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.validators import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser
from .tasks import send_verification_mail, send_verification_token
from .utils import get_fb_user_id, log_authentication_data


class GetSerializerBasedOnAuthType:
    auth_type_serializers = {"email": None, "socials": None}

    def get_serializer_class(self):
        auth_type = self.request.data.get("auth_type")
        if not auth_type:
            raise ParseError("Please provide auth_type")
        elif auth_type == "email":
            return self.auth_type_serializers["email"]
        elif auth_type == "socials":
            return self.auth_type_serializers["socials"]


class EmailRegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "is_industry_professional",
            "password",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "date_of_birth": {"required": True},
            "is_industry_professional": {"required": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data.get("password"))
        user.save()
        send_verification_mail.delay(user.id)
        return user


class SocialsRegisterUserSerializer(serializers.ModelSerializer):

    fb_token = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "is_industry_professional",
            "fb_token",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "date_of_birth": {"required": True},
            "is_industry_professional": {"required": True},
        }

    def create(self, validated_data):

        if fb_token := validated_data.pop("fb_token"):
            validated_data["fb_user_id"] = get_fb_user_id(fb_token)
        else:
            raise ParseError("Fb,google or linkedin token should be provided")

        user = CustomUser(**validated_data)
        user.save()
        send_verification_mail.delay(user.id)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "is_industry_professional",
            "is_2fa_enabled",
        ]
        read_only_fields = fields


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.is_authenticated and self.user.is_2fa_enabled:
            send_verification_token(self.user.id)
            return {"detail": "Please check email for code"}
        else:
            return data


class SocialsTokenObtainPairSerializer(EmailTokenObtainPairSerializer):

    fb_token = serializers.CharField(required=False)
    google_token = serializers.CharField(required=False)
    linkedin_token = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.CharField(required=False, default="")
        self.fields["password"] = serializers.CharField(required=False, default="")


class EmailTwoFATokenObtainPairSerializer(TokenObtainPairSerializer):
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.is_authenticated and self.user.is_2fa_enabled:
            request = self.context["request"]
            code = attrs.get("code")
            totp = pyotp.TOTP(self.user.totp_secret, interval=settings.TOTP_INTERVAL)
            if totp.verify(code):
                log_authentication_data(request, self.user)
                return data
            else:
                raise ValidationError({"detail": "Code is incorrect"})
        return data


class SocialsTwoFATokenObtainPairSerializer(EmailTwoFATokenObtainPairSerializer):

    fb_token = serializers.CharField(required=False)
    google_token = serializers.CharField(required=False)
    linkedin_token = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.CharField(required=False, default="")
        self.fields["password"] = serializers.CharField(required=False, default="")
