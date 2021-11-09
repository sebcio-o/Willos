import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "rk*j8$(^1@11xe01@5*8d4gu8#a8s$@w**$s&iwdz$st1lb+&n"

DEBUG = bool(os.environ.get("DEBUG", False))

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get("ALLOWED_HOSTS", "").split(",") if host
]

DOMAIN = "Willos"

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
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
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

RABBITMQ_DEFAULT_USER = os.environ.get("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS")

CELERY_TIMEZONE = "Europe/London"
CELERY_BROKER_URL = (
    f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@rabbitmq:5672"
)

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_DOMAIN = os.environ.get("AWS_S3_DOMAIN")
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_S3_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_DOMAIN}"
AWS_DEFAULT_ACL = "public-read"

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_S3_DOMAIN:
    STATIC_LOCATION = "static"
    STATIC_URL = f"https://{AWS_S3_DOMAIN}/{STATIC_LOCATION}/"
    STATICFILES_STORAGE = "backend.storage_backends.StaticStorage"

    PUBLIC_MEDIA_LOCATION = "media"
    MEDIA_URL = f"https://{AWS_S3_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/"
    DEFAULT_FILE_STORAGE = "backend.storage_backends.PublicMediaStorage"
else:
    STATIC_URL = "/staticfiles/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_URL = "/mediafiles/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ]
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=99),
}
CORS_ORIGIN_ALLOW_ALL = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

TOTP_INTERVAL = 120

FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

AUTH_USER_MODEL = "users.CustomUser"
