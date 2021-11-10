import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from .models import Property
from .serializers import PropertySerializer


class PropertyViewSetSchemaCreate(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                default="Bearer <TOKEN>",
            ),
            openapi.Parameter(
                "Data", openapi.IN_QUERY, required=True, type=openapi.TYPE_OBJECT
            ),
        ]


class PropertyViewSetSchemaDestroy(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                default="Bearer <TOKEN>",
            )
        ]


class PropertyViewSetSchemaList(SwaggerAutoSchema):
    def add_manual_parameters(self, parameters):
        return [
            openapi.Parameter(
                "address", openapi.IN_QUERY, required=True, type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "sale_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=Property.SaleTypes.values,
            ),
            openapi.Parameter(
                "property_type", openapi.IN_QUERY, type=openapi.TYPE_STRING
            ),
            openapi.Parameter("price_min", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("price_max", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter(
                "bedrooms_min", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "bedrooms_max", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "bathrooms_min", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "bathrooms_max", openapi.IN_QUERY, type=openapi.TYPE_INTEGER
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
                            "WKT - POLYGON", type=openapi.TYPE_STRING
                        ),
                    },
                ),
            )
        }


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    @swagger_auto_schema(auto_schema=PropertyViewSetSchemaCreate)
    @method_decorator(login_required)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @method_decorator(login_required)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @method_decorator(login_required)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=PropertyViewSetSchemaDestroy)
    @method_decorator(login_required)
    def destroy(self, request, *args, **kwargs):
        agent = get_object_or_404(Property, id=kwargs.get("pk")).agent
        if request.user == agent.customuser_set.first():
            return super().destroy(request, *args, **kwargs)
        raise ParseError("User isn't in agency that owns this property")

    @swagger_auto_schema(auto_schema=PropertyViewSetSchemaList)
    def list(self, request):

        """Use this endpoint to retrieve properties from provided address in UK"""

        address = request.query_params.get("address")
        if not address:
            return Response(status=status.HTTP_404_NOT_FOUND)

        results = requests.get(
            f"https://nominatim.openstreetmap.org/search?q={address}"
            "&format=json&country=United Kingdom&polygon_text=1&limit=3"
        ).json()
        is_polygon = False
        for place in results:
            geotext = place.get("geotext")
            if "POLYGON" in geotext:
                is_polygon = True
                break
        if not is_polygon:
            return Response(status=status.HTTP_404_NOT_FOUND)

        query = Property.objects.filter(cordinates__intersects=geotext)

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
            date = timezone.now() - timezone.timedelta(days=1)
            query = query.filter(date__gt=date)
        elif days_old == "3d":
            date = timezone.now() - timezone.timedelta(days=3)
            query = query.filter(date__gt=date)
        elif days_old == "7d":
            date = timezone.now() - timezone.timedelta(days=7)
            query = query.filter(date__gt=date)
        elif days_old == "14d":
            date = timezone.now() - timezone.timedelta(days=14)
            query = query.filter(date__gt=date)
        elif days_old == "30d":
            date = timezone.now() - timezone.timedelta(days=30)
            query = query.filter(date__gt=date)

        serializer = PropertySerializer(query, many=True)
        ctx = {"properties": serializer.data, "cordinates": geotext}
        return Response(ctx, status=status.HTTP_200_OK)
