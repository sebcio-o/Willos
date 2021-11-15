import requests
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import ParseError
from user_agents import parse

from .models import AuthenticationData

Token = PasswordResetTokenGenerator()


def log_authentication_data(request, user):
    data = parse(request.META["HTTP_USER_AGENT"])
    AuthenticationData.objects.create(
        user=user,
        ip_address=request.META["REMOTE_ADDR"],
        operating_system=data.os.family,
        device=data.device.family,
        browser=data.browser.family,
    )


def get_fb_user_id(token):
    r = requests.get(
        f"https://graph.facebook.com/debug_token?input_token={token}&access_token={settings.FACEBOOK_ACCESS_TOKEN}"
    ).json()
    data = r.get("data")

    if (error := r.get("error")) or data.get("error"):
        raise ParseError(error["message"])
    if data["is_valid"] and data["type"] == "USER":
        return data.get("user_id")
    return
