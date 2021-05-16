from django.contrib import admin

from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "address",
        "price",
        "date",
        "bedrooms",
        "bathrooms",
        "cordinates",
    )
