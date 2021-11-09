from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .helpers import GetSerializerBasedOnAuthType
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import (
    EmailRegisterUserSerializer,
    EmailTokenObtainPairSerializer,
    EmailTwoFATokenObtainPairSerializer,
    SocialsRegisterUserSerializer,
    SocialsTokenObtainPairSerializer,
    SocialsTwoFATokenObtainPairSerializer,
)
from .tasks import send_verification_mail
from .utils import Token


class UserViewPostSchema(SwaggerAutoSchema):
    """
    Register user with Email or Facebook
    """

    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "auth_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["socials", "email"],
                required=True,
            ),
            openapi.Parameter(
                "email", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "first_name", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "last_name", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "date_of_birth",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "is_industry_professional",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=True,
            ),
            openapi.Parameter("password", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("fb_token", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]

    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response(
                "Registered ",
                schema=openapi.Schema(
                    "User",
                    properties={
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "date_of_birth": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_industry_professional": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN
                        ),
                        "is_2fa_enabled": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
        }


class UserViewGetSchema(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "Authorizaton",
                openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                default="Bearer <TOKEN>",
                required=True,
            )
        ]

    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response(
                "Get currently authenticated user data",
                schema=openapi.Schema(
                    "User",
                    properties={
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "date_of_birth": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_industry_professional": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN
                        ),
                        "is_2fa_enabled": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
        }


class UserView(GetSerializerBasedOnAuthType, generics.CreateAPIView):
    models = CustomUser
    auth_type_serializers = {
        "email": EmailRegisterUserSerializer,
        "socials": SocialsRegisterUserSerializer,
    }

    def get_serializer_class(self):
        if self.request.method == "GET":
            return EmailRegisterUserSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(auto_schema=UserViewPostSchema)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=UserViewGetSchema)
    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        user_data = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": user.date_of_birth,
            "is_industry_professional": user.is_industry_professional,
            "is_2fa_enabled": user.is_2fa_enabled,
        }
        return Response(user_data, status=status.HTTP_200_OK)


class CustomTokenObtainPairViewSchema(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "auth_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["socials", "email"],
                required=True,
            ),
            openapi.Parameter(
                "fb_token",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "password",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
        ]

    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response(
                "Get JWT",
                openapi.Schema(
                    "JWT",
                    properties={
                        "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
            "401": openapi.Response(
                "Invalid credentials",
                openapi.Schema(
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default="No active account found with the given credentials",
                        ),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
        }


class CustomTokenObtainPairView(GetSerializerBasedOnAuthType, TokenObtainPairView):
    auth_type_serializers = {
        "email": EmailTokenObtainPairSerializer,
        "socials": SocialsTokenObtainPairSerializer,
    }

    @swagger_auto_schema(auto_schema=CustomTokenObtainPairViewSchema)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmailLookupViewSchema(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "email", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
        ]

    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response(
                "Email verified",
            ),
            "404": openapi.Response(
                "Invalid credentials",
                openapi.Schema(
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default="Email doesn't exists",
                        ),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
        }


class EmailLookupView(APIView):
    @swagger_auto_schema(auto_schema=EmailLookupViewSchema)
    def get(self, request):
        email = request.query_params.get("email")
        if email:
            if CustomUser.objects.filter(email=email):
                return Response(status=status.HTTP_200_OK)
            return Response(
                {"detail": "Email doesn't exists"}, status.HTTP_404_NOT_FOUND
            )
        return Response({"detail": "Please provide email"}, status.HTTP_400_BAD_REQUEST)


class SendVerificationMailViewSchema(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "email", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
        ]

    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response("Email verfied"),
            "400": openapi.Response(
                "Email already verified",
                openapi.Schema(
                    type=openapi.TYPE_STRING, default="Email already verified"
                ),
                type=openapi.TYPE_OBJECT,
            ),
        }


class SendVerificationMailView(APIView):
    @swagger_auto_schema(auto_schema=SendVerificationMailViewSchema)
    def post(self, request):
        if email := request.data.get("email"):
            user = get_object_or_404(CustomUser, email=email)
            if user.is_email_verified:
                return Response(
                    {"detail": "Email already verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Email isn't supplied"}, status=status.HTTP_400_BAD_REQUEST
            )

        send_verification_mail(user.id)
        return Response(status=status.HTTP_200_OK)


class VerifyEmailViewSchema(SwaggerAutoSchema):
    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response("Email verfied"),
        }


class VerifyEmailView(APIView):
    @swagger_auto_schema(auto_schema=VerifyEmailViewSchema)
    def get(self, request, uid, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and Token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TwoFATokenObtainPairViewSchema(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "auth_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["socials", "email"],
                required=True,
            ),
            openapi.Parameter(
                "code", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "fb_token",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "password",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
        ]

    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response(
                "Get JWT",
                openapi.Schema(
                    "JWT",
                    properties={
                        "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
            "401": openapi.Response(
                "Invalid credentials",
                openapi.Schema(
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default="No active account found with the given credentials",
                        ),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
        }


class TwoFATokenObtainPairView(GetSerializerBasedOnAuthType, TokenObtainPairView):
    auth_type_serializers = {
        "email": EmailTwoFATokenObtainPairSerializer,
        "socials": SocialsTwoFATokenObtainPairSerializer,
    }

    @swagger_auto_schema(auto_schema=TwoFATokenObtainPairViewSchema)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TwoFAViewSchema(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "Authorizaton",
                openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                default="Bearer <TOKEN>",
                required=True,
            ),
            openapi.Parameter(
                "is_2fa_enabled",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=True,
            ),
        ]

    def get_response_schemas(self, response_serializers):
        return {
            "200": openapi.Response(
                "Set 2fa",
                openapi.Schema(
                    properties={
                        "is_2fa_enabled": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
            "400": openapi.Response(
                "Email isn't verified",
                openapi.Schema(
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default="Please verify email first",
                        ),
                    },
                    type=openapi.TYPE_OBJECT,
                ),
            ),
        }


class TwoFAView(generics.GenericAPIView):
    @swagger_auto_schema(auto_schema=TwoFAViewSchema)
    @method_decorator(login_required)
    def put(self, request):
        """
        Set is_2fa_enabled for currently authenticated user
        """
        user = request.user
        is_2fa_enabled = request.data.get("is_2fa_enabled")
        if is_2fa_enabled and user.is_email_verified:
            user.is_2fa_enabled = is_2fa_enabled
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Please verify email first"},
                status=status.HTTP_400_BAD_REQUEST,
            )
