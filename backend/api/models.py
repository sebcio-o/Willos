from datetime import datetime

from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from backend.storage_backends import PublicMediaStorage


class RealEstateAgent(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=16)
    descripton = models.TextField()
    cordinates = models.PointField()


class Property(models.Model):
    class SaleTypes(models.TextChoices):
        FOR_SALE = "for_sale", "For sale"
        TO_RENT = "to_rent", "To rent"

    sale_type = models.CharField(max_length=8, choices=SaleTypes.choices)
    thumbnail = models.ImageField(storage=PublicMediaStorage)
    title = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    price = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(500_000_000)]
    )
    date = models.DateTimeField(default=timezone.now)
    property_type = models.CharField(max_length=25)
    bedrooms = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    bathrooms = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    sqft = models.IntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(10_000)]
    )
    description = models.CharField(max_length=1024)
    key_features = models.JSONField(null=True)
    cordinates = models.PointField()
    agent = models.ForeignKey(RealEstateAgent, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
