import requests
from django.contrib.gis.geos import Polygon
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
        serializer = PropertySerializer(query, many=True)
        ctx = {"properties": serializer.data, "cordinates": bbox}
        return Response(ctx, status=status.HTTP_200_OK)
