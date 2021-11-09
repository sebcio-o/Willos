from django.urls import path

from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    EmailLookupView,
    SendVerificationMailView,
    TwoFATokenObtainPairView,
    TwoFAView,
    UserView,
    VerifyEmailView,
)

urlpatterns = [
    path("", UserView.as_view(), name="user"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "token/code/",
        TwoFATokenObtainPairView.as_view(throttle_classes=[AnonRateThrottle]),
        name="code_token_obtain_pair",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("email/", EmailLookupView.as_view(), name="email"),
    path(
        "email/verify/",
        SendVerificationMailView.as_view(),
        name="send_verification_mail",
    ),
    path("email/verify/<uid>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("2fa/", TwoFAView.as_view(), name="2fa"),
]
