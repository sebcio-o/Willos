from django.contrib import admin

from .models import AuthenticationData, CustomUser

admin.site.register([CustomUser, AuthenticationData])
