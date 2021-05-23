from datetime import time

import requests
from django.contrib.gis.geos import Polygon
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import Property
from .serializers import PropertySerializer


class PropertyViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def list(self, request):

        address = request.query_params.get("address")
        if not address:
            return Response(status=status.HTTP_404_NOT_FOUND)

        geojson = (
            requests.get(
                f"https://nominatim.openstreetmap.org/search?q={address}"
                "&format=json&country=United Kingdom&polygon_geojson=1&limit=1"
            )
            .json()[0]
            .get("geojson")
        )

        if geojson and "Polygon" in geojson.get("type"):
            bbox = geojson.get("coordinates")
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        poly = Polygon(tuple((x, y) for x, y in bbox[0]))
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
        ctx = {"properties": serializer.data, "cordinates": bbox}
        return Response(ctx, status=status.HTTP_200_OK)
