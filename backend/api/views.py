import requests
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import Property
from .serializers import PropertySerializer


class PropertyViewSetSchema(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "address",
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "sale_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=Property.SaleTypes.values,
            ),
            openapi.Parameter(
                "property_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "price_min",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "price_max",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "bedrooms_min",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "bedrooms_max",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "bathrooms_min",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "bathrooms_max",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "days_old",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["1d", "3d", "7d", "14d", "30d"],
            ),
        ]

    def get_response_serializers(self):
        return {
            "200": openapi.Response(
                "Get properties and cordinates from address",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "properties": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=self.serializer_to_schema(PropertySerializer({})),
                        ),
                        "cordinates": openapi.Schema(
                            "WKT - POLYGON",
                            type=openapi.TYPE_STRING,
                        ),
                    },
                ),
            ),
        }


class PropertyViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    @swagger_auto_schema(auto_schema=PropertyViewSetSchema)
    def list(self, request):

        """Use this endpoint to retrieve properties from provided address in UK"""

        address = request.query_params.get("address")
        if not address:
            return Response(status=status.HTTP_404_NOT_FOUND)

        poly = (
            requests.get(
                f"https://nominatim.openstreetmap.org/search?q={address}"
                "&format=json&country=United Kingdom&polygon_text=1&limit=1"
            )
            .json()[0]
            .get("geotext")
        )
        if "POLYGON" not in poly:
            return Response(status=status.HTTP_404_NOT_FOUND)

        query = Property.objects.filter(cordinates__intersects=poly)

        sale_type = request.query_params.get("sale_type")
        if sale_type:
            query = query.filter(sale_type=sale_type)

        property_type = request.query_params.get("property_type")
        if property_type:
            query = query.filter(property_type=property_type)

        price_min = request.query_params.get("price_min")
        price_max = request.query_params.get("price_max")
        if price_max and price_min:
            query = query.filter(price__lte=int(price_max), price__gte=int(price_min))
        elif price_max:
            query = query.filter(price__lte=int(price_max))
        elif price_min:
            query = query.filter(price__gte=int(price_min))

        bedrooms_min = request.query_params.get("bedrooms_min")
        bedrooms_max = request.query_params.get("bedrooms_max")
        if bedrooms_max and bedrooms_min:
            query = query.filter(
                bedrooms__lte=int(bedrooms_max), bedrooms__gte=int(bedrooms_min)
            )
        elif bedrooms_max:
            query = query.filter(bedrooms__lte=int(bedrooms_max))
        elif bedrooms_min:
            query = query.filter(bedrooms__gte=int(bedrooms_min))

        bathrooms_min = request.query_params.get("bathrooms_min")
        bathrooms_max = request.query_params.get("bathrooms_max")
        if bathrooms_max and bathrooms_min:
            query = query.filter(
                bathrooms__lte=int(bathrooms_max), bathrooms__gte=int(bathrooms_min)
            )
        elif bathrooms_max:
            query = query.filter(bathrooms__lte=int(bathrooms_max))
        elif bathrooms_min:
            query = query.filter(bathrooms__gte=int(bathrooms_min))

        days_old = request.query_params.get("days_old")
        if days_old == "1d":
            date = timezone.now() + timezone.timedelta(1)
            query = query.filter(date__lt=date)
        elif days_old == "3d":
            date = timezone.now() + timezone.timedelta(3)
            query = query.filter(date__lt=date)
        elif days_old == "7d":
            date = timezone.now() + timezone.timedelta(7)
            query = query.filter(date__lt=date)
        elif days_old == "14d":
            date = timezone.now() + timezone.timedelta(14)
            query = query.filter(date__lt=date)
        elif days_old == "30d":
            date = timezone.now() + timezone.timedelta(30)
            query = query.filter(date__lt=date)

        serializer = PropertySerializer(query, many=True)
        ctx = {"properties": serializer.data, "cordinates": poly}
        return Response(ctx, status=status.HTTP_200_OK)
