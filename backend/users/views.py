from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import decorators
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

import pyotp
from rest_framework import generics, status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
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


class UserView(generics.CreateAPIView):
    models = User

    def get_serializer_class(self):
        if self.request.POST.get("auth_type") == "socials":
            return SocialsRegisterUserSerializer
        else:
            return EmailRegisterUserSerializer

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


class CustomTokenObtainPairView(TokenObtainPairView):
    def get_serializer_class(self):
        auth_type = self.request.data.get("auth_type")
        if not auth_type:
            raise ParseError("Please provide auth_type")
        elif auth_type == "email":
            return EmailTokenObtainPairSerializer
        elif auth_type == "socials":
            return SocialsTokenObtainPairSerializer


class EmailLookupView(APIView):
    def get(self, request):
        email = request.query_params.get("email")
        if email:
            if User.objects.filter(email=email):
                return Response(status=status.HTTP_200_OK)
            return Response(
                {"detail": "Email doesn't exists"}, status.HTTP_404_NOT_FOUND
            )
        return Response({"detail": "Please provide email"}, status.HTTP_400_BAD_REQUEST)


class SendVerificationMailView(APIView):
    def post(self, request):
        if email := request.data.get("email"):
            user = get_object_or_404(User, email=email)
            if user.is_email_verified:
                return Response(
                    {"detail": "Email already verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Email aint supplied"}, status=status.HTTP_400_BAD_REQUEST
            )

        send_verification_mail(user.id)
        return Response(status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    def get(self, request, uid, token):
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and Token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TwoFATokenObtainPairView(TokenObtainPairView):
    def get_serializer_class(self):
        auth_type = self.request.data.get("auth_type")
        if not auth_type:
            raise ParseError("Please provide auth_type")
        elif auth_type == "email":
            return EmailTwoFATokenObtainPairSerializer
        elif auth_type == "socials":
            return SocialsTwoFATokenObtainPairSerializer


class TwoFAView(generics.RetrieveUpdateAPIView):
    @method_decorator(login_required)
    def put(self, request):
        user = request.user
        is_2fa_enabled = request.data.get("is_2fa_enabled")
        if is_2fa_enabled and user.is_email_verified:
            user.is_2fa_enabled = is_2fa_enabled
            user.totp_secret = pyotp.random_base32()
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Please verify email first"},
                status=status.HTTP_400_BAD_REQUEST,
            )
