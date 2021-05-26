import pytest
import requests
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker


@pytest.mark.django_db
class TestPropertyView:
    def test_search_by_address(self, client):
        data = requests.get(
            "https://nominatim.openstreetmap.org/search?q=London"
            "&format=json&country=United Kingdom&polygon_geojson=1&limit=1"
        ).json()[0]
        baker.make(
            "api.Property", cordinates=Point(float(data["lon"]), float(data["lat"]))
        )
        response = client.get(reverse("properties-list"), {"address": "London"})
        assert response.status_code == 200
        assert len(response.data["properties"]) == 1

    def test_search_by_sale_type(self, client):
        baker.make(
            "api.Property",
            cordinates=Point(-0.1276474, 51.5073219),
            sale_type="for-sale",
        )
        baker.make(
            "api.Property",
            cordinates=Point(-0.1276474, 51.5073219),
            sale_type="to-rent",
        )
        response = client.get(
            reverse("properties-list"), {"address": "London", "sale_type": "for-sale"}
        )
        assert len(response.data["properties"]) == 1
        response = client.get(
            reverse("properties-list"), {"address": "London", "sale_type": "to-rent"}
        )
        assert len(response.data["properties"]) == 1

    def test_search_by_property_type(self, client):
        baker.make(
            "api.Property",
            cordinates=Point(-0.1276474, 51.5073219),
            property_type="Land",
        )
        response = client.get(
            reverse("properties-list"), {"address": "London", "property_type": "Land"}
        )
        assert len(response.data["properties"]) == 1

    def test_search_by_price(self, client):
        baker.make("api.Property", cordinates=Point(-0.1276474, 51.5073219), price=1000)
        response = client.get(
            reverse("properties-list"), {"address": "London", "price_max": "999"}
        )
        assert len(response.data["properties"]) == 0
        response = client.get(
            reverse("properties-list"), {"address": "London", "price_min": "1001"}
        )
        assert len(response.data["properties"]) == 0
        response = client.get(
            reverse("properties-list"),
            {"address": "London", "price_min": "999", "price_max": "1001"},
        )
        assert len(response.data["properties"]) == 1

    def test_search_by_bedrooms(self, client):
        baker.make("api.Property", cordinates=Point(-0.1276474, 51.5073219), bedrooms=5)
        response = client.get(
            reverse("properties-list"), {"address": "London", "bedrooms_max": "4"}
        )
        assert len(response.data["properties"]) == 0
        response = client.get(
            reverse("properties-list"), {"address": "London", "bedrooms_min": "6"}
        )
        assert len(response.data["properties"]) == 0
        response = client.get(
            reverse("properties-list"),
            {"address": "London", "bedrooms_min": "4", "bedrooms_max": "6"},
        )
        assert len(response.data["properties"]) == 1

    def test_search_by_bathrooms(self, client):
        baker.make(
            "api.Property", cordinates=Point(-0.1276474, 51.5073219), bathrooms=5
        )
        response = client.get(
            reverse("properties-list"), {"address": "London", "bathrooms_max": "4"}
        )
        assert len(response.data["properties"]) == 0
        response = client.get(
            reverse("properties-list"), {"address": "London", "bathrooms_min": "6"}
        )
        assert len(response.data["properties"]) == 0
        response = client.get(
            reverse("properties-list"),
            {"address": "London", "bathrooms_min": "4", "bathrooms_max": "6"},
        )
        assert len(response.data["properties"]) == 1

    def test_search_by_daysold(self, client):

        now = timezone.now()
        dates_to_create = [
            now,
            now + timezone.timedelta(days=2),
            now + timezone.timedelta(days=4),
            now + timezone.timedelta(days=8),
            now + timezone.timedelta(days=15),
            now + timezone.timedelta(days=31),
        ]
        for date in dates_to_create:
            baker.make(
                "api.Property", cordinates=Point(-0.1276474, 51.5073219), date=date
            )

        response = client.get(
            reverse("properties-list"), {"address": "London", "days_old": "1d"}
        )
        assert len(response.data["properties"]) == 1

        response = client.get(
            reverse("properties-list"), {"address": "London", "days_old": "3d"}
        )
        assert len(response.data["properties"]) == 2

        response = client.get(
            reverse("properties-list"), {"address": "London", "days_old": "7d"}
        )
        assert len(response.data["properties"]) == 3

        response = client.get(
            reverse("properties-list"), {"address": "London", "days_old": "14d"}
        )
        assert len(response.data["properties"]) == 4

        response = client.get(
            reverse("properties-list"), {"address": "London", "days_old": "30d"}
        )
        assert len(response.data["properties"]) == 5

        response = client.get(reverse("properties-list"), {"address": "London"})
        assert len(response.data["properties"]) == 6
