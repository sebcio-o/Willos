from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken


from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import pyotp

from ..utils import Token

import pytest
from model_bakery import baker


@pytest.mark.django_db
class TestPropertyView:
    def setup(self):
        self.client = APIClient()
        self.user_model = get_user_model()

    def test_registration_email(self):
        response = self.client.post(
            "http://localhost:8000/api/users/",
            {
                "auth_type": "email",
                "username": "zbychu",
                "email": "testq@gmail.com",
                "first_name": "Sebcio",
                "last_name": "Ozi",
                "date_of_birth": "2012-09-04 00:00",
                "is_industry_professional": True,
                "password": "MoiDrodzyRekturerzy123",
            },
            format="json",
        )
        data = response.json()

        assert response.status_code == 201
        assert len(data) == 5

    def test_registration_facebook(self, fb_user_token):

        response = self.client.post(
            "http://localhost:8000/api/users/",
            {
                "auth_type": "socials",
                "username": "zbychu",
                "email": "testq1@gmail.com",
                "first_name": "Sebcio",
                "last_name": "Ozi",
                "date_of_birth": "2012-09-04 00:00",
                "is_industry_professional": True,
                "fb_token": fb_user_token,
            },
            format="json",
        )
        data = response.json()
        print(data)
        assert response.status_code == 201
        assert len(data) == 5

    def test_registraion_user_already_exist(self):
        response = self.client.post(
            "http://localhost:8000/api/users/",
            {
                "username": "zbychu",
                "email": "test@gmail.com",
                "first_name": "Sebcio",
                "last_name": "Ozi",
                "date_of_birth": "2012-09-04 00:00",
                "is_industry_profesional": True,
                "password": "MoiDrodzyRekturerzy123",
            },
            format="json",
        )
        data = response.json()

        assert response.status_code == 400
        assert len(data) == 1

    def test_registraion_without_auth_type(self):

        response = self.client.post(
            "http://localhost:8000/api/users/",
            {
                "username": "zbychu",
                "email": "test@gmail.com",
                "first_name": "Sebcio",
                "last_name": "Ozi",
                "date_of_birth": "2012-09-04 00:00",
                "is_industry_profesional": True,
                "password": "MoiDrodzyRekturerzy123",
            },
            format="json",
        )
        data = response.json()

        assert response.status_code == 400
        assert len(data) == 1

    def test_get_authenticated_user(self, user):

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.get("http://localhost:8000/api/users/", format="json")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 6

    def test_get_tokens_with_email(self, user):

        self.client.credentials(HTTP_USER_AGENT="Linux")
        response = self.client.post(
            "http://localhost:8000/api/users/token/",
            {
                "auth_type": "email",
                "email": "testq@gmail.com",
                "password": "MoiDrodzyRekturerzy123",
            },
            format="json",
        )
        assert len(response.data) == 2

    def test_get_tokens_with_facebook(self, fb_user, fb_user_token):

        self.client.credentials(HTTP_USER_AGENT="Linux")
        response = self.client.post(
            "http://localhost:8000/api/users/token/",
            {"auth_type": "socials", "fb_token": fb_user_token},
            format="json",
        )
        assert len(response.data) == 2

    def test_get_tokens_with_email_and_2fa(self, user):

        user.is_email_verified = True
        user.is_2fa_enabled = True
        user.totp_secret = pyotp.random_base32()
        user.save()

        body = {
            "auth_type": "email",
            "email": "testq@gmail.com",
            "password": "MoiDrodzyRekturerzy123",
        }

        self.client.credentials(HTTP_USER_AGENT="Linux")
        response = self.client.post(
            "http://localhost:8000/api/users/token/",
            body,
            format="json",
        )

        assert response.data["detail"] == "Please check email for code"

        body["code"] = pyotp.TOTP(
            user.totp_secret, interval=settings.TOTP_INTERVAL
        ).now()
        response = self.client.post(
            "http://localhost:8000/api/users/token/code/",
            body,
            format="json",
        )

        assert len(response.data) == 2

    def test_get_tokens_with_fb_and_2fa(self, fb_user, fb_user_token):

        fb_user.is_email_verified = True
        fb_user.is_2fa_enabled = True
        fb_user.totp_secret = pyotp.random_base32()
        fb_user.save()

        body = {
            "auth_type": "socials",
            "email": "testq@gmail.com",
            "fb_token": fb_user_token,
        }

        self.client.credentials(HTTP_USER_AGENT="Linux")
        response = self.client.post(
            "http://localhost:8000/api/users/token/",
            body,
            format="json",
        )

        assert response.data["detail"] == "Please check email for code"

        body["code"] = pyotp.TOTP(
            fb_user.totp_secret, interval=settings.TOTP_INTERVAL
        ).now()
        response = self.client.post(
            "http://localhost:8000/api/users/token/code/",
            body,
            format="json",
        )
        assert len(response.data) == 2

    def test_enable_2fa(self, user):

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.put(
            "http://localhost:8000/api/users/2fa/",
            {"is_2fa_enabled": True},
            format="json",
        )

        assert response.json() == {"detail": "Please verify email first"}

        user.is_email_verified = True
        user.save()

        response = self.client.put(
            "http://localhost:8000/api/users/2fa/",
            {"is_2fa_enabled": True},
            format="json",
        )
        assert response.status_code == 200

    def test_email(self, user):

        response = self.client.get(
            "http://localhost:8000/api/users/email/",
            {"email": "testq@gmail.com"},
            format="json",
        )

        assert response.status_code == 200

        response = self.client.post(
            "http://localhost:8000/api/users/email/verify/",
            {"email": "testq@gmail.com"},
            format="json",
        )
        assert response.status_code == 200

        uid = (urlsafe_base64_encode(force_bytes(user.id)),)
        token = Token.make_token(user)
        response = self.client.get(
            f"http://localhost:8000/api/users/email/verify/{uid}/{token}/",
            format="json",
        )
        assert response.status_code == 200
