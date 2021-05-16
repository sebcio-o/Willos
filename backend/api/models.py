from django.contrib.gis.db import models


class Property(models.Model):
    url = models.URLField(null=True)
    thumbnail = models.URLField(null=True)
    title = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=100, null=True)
    price = models.IntegerField(null=True)
    date = models.DateTimeField(null=True)
    agent_name = models.CharField(max_length=50, null=True)
    agent_phone = models.CharField(max_length=50, null=True)
    agent_address = models.CharField(max_length=100, null=True)
    property_type = models.CharField(max_length=25, null=True)
    bedrooms = models.IntegerField(null=True)
    bathrooms = models.IntegerField(null=True)
    receptionrooms = models.IntegerField(null=True)
    sqft = models.CharField(max_length=15, null=True)
    description = models.TextField(null=True)
    key_features = models.JSONField(null=True)
    cordinates = models.PointField(null=True)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
