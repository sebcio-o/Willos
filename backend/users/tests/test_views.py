import os

import pyotp
import pytest
from django.conf import settings
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from helpers import get_domain
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser


from ..utils import Token


@pytest.mark.django_db
class TestPropertyView:
    def setup(self):
        self.client = APIClient()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_register_user_with_email(self, registration_data):
        response = self.client.post(reverse("users"), registration_data, format="json")
        data = response.json()
        assert response.status_code == 201
        assert len(data) == 5
        users = CustomUser.objects.filter(email=registration_data["email"])
        assert users.count() == 1
        assert len(mail.outbox) == 1

    def test_register_user_with_wrong_email(self, registration_data):
        registration_data["email"] = "1232321"
        response = self.client.post(reverse("users"), registration_data, format="json")

        assert response.status_code == 400
        user = CustomUser.objects.filter(email=registration_data["email"])
        assert user.exists() is False

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_register_user_with_facebook(self, registration_data):
        registration_data["auth_type"] = "socials"
        registration_data["fb_token"] = os.environ["FACEBOOK_TEST_USER_TOKEN"]
        response = self.client.post(reverse("users"), registration_data, format="json")
        data = response.json()
        assert response.status_code == 201, data["detail"]
        assert len(data) == 5
        users = CustomUser.objects.filter(email=registration_data["email"])
        assert users.count() == 1
        assert len(mail.outbox) == 1

    def test_register_user_that_already_exist(self, registration_data, user):
        response = self.client.post(reverse("users"), registration_data, format="json")
        data = response.json()
        assert response.status_code == 400
        assert len(data) == 1
        assert "email" in data

    def test_register_user_without_auth_type(self, registration_data):
        registration_data["auth_type"] = ""
        response = self.client.post(reverse("users"), registration_data, format="json")
        data = response.json()
        assert response.status_code == 400
        assert data["detail"] == "Please provide auth_type", data["detail"]

    def test_get_authenticated_user_data(self, user):

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.get(reverse("users"), format="json")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 6

    def test_get_tokens_with_email(self, user, registration_data):

        self.client.credentials(HTTP_USER_AGENT="Linux")
        data = self.client.post(
            reverse("token_obtain_pair"), registration_data, format="json"
        ).json()
        assert len(data) == 2
        assert "refresh" in data
        assert "access" in data

    def test_get_tokens_with_facebook(self, user):

        self.client.credentials(HTTP_USER_AGENT="Linux")
        data = self.client.post(
            reverse("token_obtain_pair"),
            {
                "auth_type": "socials",
                "fb_token": os.environ["FACEBOOK_TEST_USER_TOKEN"],
            },
            format="json",
        ).json()
        assert len(data) == 2
        assert "refresh" in data
        assert "access" in data

    def test_get_tokens_with_email_and_2fa_enabled(self, user, registration_data):

        user.is_email_verified = True
        user.is_2fa_enabled = True
        user.totp_secret = pyotp.random_base32()
        user.save()

        self.client.credentials(HTTP_USER_AGENT="Linux")
        response = self.client.post(
            reverse("token_obtain_pair"), registration_data, format="json"
        )

        assert response.data["detail"] == "Please check email for code"

        registration_data["code"] = pyotp.TOTP(
            user.totp_secret, interval=settings.TOTP_INTERVAL
        ).now()
        data = self.client.post(
            reverse("code_token_obtain_pair"), registration_data, format="json"
        ).json()

        assert len(data) == 2
        assert "refresh" in data
        assert "access" in data

    def test_get_tokens_with_fb_and_2fa_enabled(self, user, registration_data):

        user.is_email_verified = True
        user.is_2fa_enabled = True
        user.totp_secret = pyotp.random_base32()
        user.save()

        registration_data["auth_type"] = "socials"
        registration_data["fb_token"] = os.environ["FACEBOOK_TEST_USER_TOKEN"]

        self.client.credentials(HTTP_USER_AGENT="Linux")
        response = self.client.post(
            reverse("token_obtain_pair"), registration_data, format="json"
        )

        assert response.data["detail"] == "Please check email for code"

        registration_data["code"] = pyotp.TOTP(
            user.totp_secret, interval=settings.TOTP_INTERVAL
        ).now()
        data = self.client.post(
            reverse("code_token_obtain_pair"), registration_data, format="json"
        ).json()
        assert len(data) == 2
        assert "refresh" in data
        assert "access" in data

    def test_enable_2fa(self, user):

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.put(
            reverse("2fa"), {"is_2fa_enabled": True}, format="json"
        )

        assert response.json() == {"detail": "Please verify email first"}

        user.is_email_verified = True
        user.save()

        response = self.client.put(
            reverse("2fa"), {"is_2fa_enabled": True}, format="json"
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_2fa_enabled is True

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_verification(self, user, registration_data):

        response = self.client.get(reverse("email"), registration_data, format="json")

        assert response.status_code == 200

        response = self.client.post(
            reverse("send_verification_mail"), registration_data, format="json"
        )
        assert response.status_code == 200

        last_mail = mail.outbox[0]
        verification_url = last_mail.body.split("<br />\n")[1].replace(" \n", "")
        user = CustomUser.objects.get(email=registration_data["email"])
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = Token.make_token(user)
        assert last_mail.subject == "Activate your account at " + get_domain()
        assert verification_url == settings.BASE_URL + reverse(
            "verify_email", args=(uid, token)
        )

        response = self.client.get(
            reverse("verify_email", args=(uid, token)), format="json"
        )

        assert response.status_code == 200
        assert user.is_active is True
