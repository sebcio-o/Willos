import boto3
from django.conf import settings


def is_property_in_image(img):
    client = boto3.client(
        "rekognition",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
    )
    response = client.detect_labels(
        Image={"Bytes": img.file.read()},
        MaxLabels=10,
    )
    has_property = any(
        [label.get("Name") == "Building" for label in response.get("Labels", {})]
    )
    return has_property
