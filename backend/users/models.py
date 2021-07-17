from typing import Tuple

from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(validators=[EmailValidator], unique=True)
    avatar = models.ImageField("/", null=True, blank=True)
    date_of_birth = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    is_email_verified = models.BooleanField(default=False)
    is_industry_professional = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)

    totp_secret = models.CharField(max_length=32, null=True, blank=True)

    fb_user_id = models.CharField(max_length=100)
    google_user_id = models.CharField(max_length=100)
    linkedin_user_id = models.CharField(max_length=100)


class AuthenticationData(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ip_address = models.GenericIPAddressField()
    operating_system = models.CharField(max_length=100)
    device = models.CharField(max_length=100)
    browser = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField(auto_now=True)
