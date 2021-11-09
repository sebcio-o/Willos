from django.contrib.auth.backends import ModelBackend

from .models import CustomUser
from .utils import get_fb_user_id, log_authentication_data


class AuthBackend(ModelBackend):
    def _authenticate_with_email(self, request, email, password):
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            CustomUser().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                if not user.is_2fa_enabled:
                    log_authentication_data(request, user)
                return user

    def _authenticate_with_socials(self, request):
        if fb_token := request.data.get("fb_token"):
            credentials = {"fb_user_id": get_fb_user_id(fb_token)}
        else:
            return
        try:
            return CustomUser.objects.get(**credentials)
        except CustomUser.DoesNotExist:
            return

    def authenticate(self, request, **kwargs):
        if not hasattr(request, "data"):
            email = request.POST.get("username")
            password = request.POST.get("password")
            return self._authenticate_with_email(request, email, password)

        if request.data.get("auth_type") == "socials":
            return self._authenticate_with_socials(request)
        elif request.data.get("auth_type") == "email":
            email = request.data.get("email")
            password = request.data.get("password")
            return self._authenticate_with_email(request, email, password)
