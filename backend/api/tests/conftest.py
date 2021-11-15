import pytest
from django.test import Client
import requests
from model_bakery import baker
from django.contrib.gis.geos import Point


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def property():
    data = requests.get(
        "https://nominatim.openstreetmap.org/search?q=London"
        "&format=json&country=United Kingdom&polygon_geojson=1&limit=1"
    ).json()[0]
    return baker.make(
        "api.Property", cordinates=Point(float(data["lon"]), float(data["lat"]))
    )