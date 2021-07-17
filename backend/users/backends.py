from django.contrib.auth.backends import ModelBackend

from .models import User
from .utils import get_fb_user_id, log_authentication_data


class AuthBackend(ModelBackend):
    def _authenticate_with_email(self, request, email, password):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                if not user.is_2fa_enabled:
                    log_authentication_data(request, user)
                return user

    def _authenticate_with_socials(self, request):
        if fb_token := request.POST.get("fb_token"):
            credentials = {"fb_user_id": get_fb_user_id(fb_token)}
        else:
            return
        try:
            return User.objects.get(**credentials)
        except User.DoesNotExist:
            return

    def authenticate(self, request, **kwargs):
        if request.POST.get("auth_type") == "socials":
            return self._authenticate_with_socials(request)
        elif request.POST.get("auth_type") == "email":
            email = request.POST.get("username")
            password = request.POST.get("password")
            return self._authenticate_with_email(request, email, password)
