import os
from datetime import timedelta
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = bool(os.environ.get("DEBUG", False))

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get("ALLOWED_HOSTS", "").split(",") if host
]

BASE_URL = "http://localhost:8000"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "storages",
    "drf_yasg",
    "rest_framework",
    "corsheaders",
    "api.apps.ApiConfig",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "backend.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "POSTGRES_ENGINE", "django.contrib.gis.db.backends.postgis"
        ),
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}


AUTHENTICATION_BACKENDS = ["users.backends.AuthBackend"]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/London"

USE_I18N = True
USE_L10N = True
USE_TZ = True

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_DATABASE = os.environ["REDIS_DATABASE"]
REDIS_PORT = os.environ["REDIS_PORT"]

CELERY_TIMEZONE = "Europe/London"
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}"
TEST_RUNNER = "djcelery.contrib.test_runner.CeleryTestSuiteRunner"

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")
AWS_S3_OBJECT_PARAMETERS = {"ACL": "public-read", "CacheControl": "max-age=86400"}
AWS_QUERYSTRING_AUTH = False

STATIC_LOCATION = "static"
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/{STATIC_LOCATION}/"
STATICFILES_STORAGE = "backend.storage_backends.StaticStorage"

PUBLIC_MEDIA_LOCATION = "media"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/{PUBLIC_MEDIA_LOCATION}/"
DEFAULT_FILE_STORAGE = "backend.storage_backends.PublicMediaStorage"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ]
}
if DEBUG:
    SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(days=99)}
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ALLOWED_ORIGINS = ALLOWED_HOSTS


EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

TOTP_INTERVAL = 120

FACEBOOK_ACCESS_TOKEN = os.environ["FACEBOOK_ACCESS_TOKEN"]

AUTH_USER_MODEL = "users.CustomUser"

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)
