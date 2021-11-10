from rest_framework import serializers

from .models import Property
from .validators import is_property_in_image

from rest_framework.exceptions import ParseError


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
        ]
        read_only_fields = ["id"]

    def save(self, **kwargs):
        agent = self.context["request"].user.real_estate_agency
        if not agent:
            raise ParseError("This user isn't assigned to any agency")
        self.validated_data["agent"] = agent
        img = self.validated_data["thumbnail"]
        if not is_property_in_image(img):
            raise ParseError("Image doesn't contain property")
        return super().save(**kwargs)