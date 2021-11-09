from django.contrib import admin

from .models import CustomUser, AuthenticationData

admin.site.register([CustomUser, AuthenticationData])
