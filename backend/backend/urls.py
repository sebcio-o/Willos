from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(title="Willos REST API", default_version="v1")
    )

    urlpatterns += [
        re_path(
            r"^swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        )
    ]
