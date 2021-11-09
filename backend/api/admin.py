from django.contrib import admin

from .models import Property, RealEstateAgent

admin.site.register(RealEstateAgent)


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
