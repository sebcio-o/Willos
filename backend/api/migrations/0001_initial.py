# Generated by Django 3.2.2 on 2021-11-09 20:12

import backend.storage_backends
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RealEstateAgent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("address", models.CharField(max_length=256)),
                ("phone_number", models.CharField(max_length=16)),
                ("descripton", models.TextField()),
                (
                    "cordinates",
                    django.contrib.gis.db.models.fields.PointField(srid=4326),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Property",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sale_type",
                    models.CharField(
                        choices=[("for_sale", "For sale"), ("to_rent", "To rent")],
                        max_length=8,
                    ),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        storage=backend.storage_backends.PublicMediaStorage,
                        upload_to="",
                    ),
                ),
                ("title", models.CharField(max_length=50)),
                ("address", models.CharField(max_length=100)),
                (
                    "price",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1000),
                            django.core.validators.MaxValueValidator(500000000),
                        ]
                    ),
                ),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                ("property_type", models.CharField(max_length=25)),
                (
                    "bedrooms",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(20),
                        ]
                    ),
                ),
                (
                    "bathrooms",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(20),
                        ]
                    ),
                ),
                (
                    "sqft",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(10),
                            django.core.validators.MaxValueValidator(10000),
                        ]
                    ),
                ),
                ("description", models.CharField(max_length=1024)),
                ("key_features", models.JSONField(null=True)),
                (
                    "cordinates",
                    django.contrib.gis.db.models.fields.PointField(srid=4326),
                ),
                (
                    "agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.realestateagent",
                    ),
                ),
            ],
            options={"verbose_name": "Property", "verbose_name_plural": "Properties"},
        ),
    ]
