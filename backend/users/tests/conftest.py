import pytest

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

TEXT_FB_USER_TOKEN = "EAAJGURJWflgBAE7dTz7UHP0vsICsj6o77GIlVYSYZBNeZCFTcguuwbwXHByUvFL6ZCK17LospVjZAjXksZCcXkTXii43QSC02OfjQWLuJ0qdYvQLszHZCSa8hz5IUo2oejcf0bm9QR8eert7MvLavpypkNrS9bL6FEwpKYgjPG672RDIiyFZCMVl3fSV0ZBMGZAqXCprSi9EvXj5kTZCbL2GnD"
user_model = get_user_model()


@pytest.fixture
def user():
    user = user_model.objects.create_user(
        username="zbychu",
        email="testq@gmail.com",
        password="MoiDrodzyRekturerzy123",
    )
    return user


@pytest.fixture
def fb_user():
    client = APIClient()
    response = client.post(
        "http://localhost:8000/api/users/",
        {
            "auth_type": "socials",
            "username": "zbychu",
            "email": "testq@gmail.com",
            "first_name": "Sebcio",
            "last_name": "Ozi",
            "date_of_birth": "2012-09-04 00:00",
            "is_industry_professional": True,
            "fb_token": TEXT_FB_USER_TOKEN,
        },
        format="json",
    )
    return user_model.objects.get(email=response.json().get("email"))


@pytest.fixture
def fb_user_token():
    return TEXT_FB_USER_TOKEN
