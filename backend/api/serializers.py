from rest_framework import serializers

from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "id",
            "sale_type",
            "thumbnail",
            "title",
            "address",
            "price",
            "property_type",
            "bedrooms",
            "bathrooms",
            "sqft",
            "description",
            "key_features",
            "cordinates",
            "agent",
        ]
        read_only_fields = ["id"]
