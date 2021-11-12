import pyotp
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from helpers import get_domain

from .models import CustomUser
from .utils import Token


@shared_task
def send_verification_mail(id):
    user = CustomUser.objects.get(id=id)
    message = render_to_string(
        "email_verification.html",
        {
            "user": user,
            "url": settings.BASE_URL,
            "uid": urlsafe_base64_encode(force_bytes(id)),
            "token": Token.make_token(user),
        },
    )
    send_mail(
        "Activate your account at " + get_domain(),
        message,
        "noreply@gmail.com",
        [user.email],
    )


@shared_task
def send_verification_token(id):
    domain = get_domain()
    user = CustomUser.objects.get(id=id)
    totp = pyotp.TOTP(user.totp_secret, interval=settings.TOTP_INTERVAL)
    message = render_to_string(
        "2fa_verification.html", {"user": user, "domain": domain, "token": totp.now()}
    )
    send_mail(
        "Continue to sign in at " + domain, message, "noreply@gmail.com", [user.email]
    )
