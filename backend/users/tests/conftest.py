import pytest

from users.models import CustomUser


@pytest.fixture
def registration_data():
    return {
        "auth_type": "email",
        "username": "zdddb111y",
        "email": "test1111@gmail.com",
        "first_name": "Sebcio",
        "last_name": "Ozi",
        "date_of_birth": "2001-09-04 00:00",
        "is_industry_professional": True,
        "password": "MoiDrodzyRekturerzy123",
    }


@pytest.fixture
def user(registration_data):
    return CustomUser.objects.create_user(
        username=registration_data["username"],
        email=registration_data["email"],
        password=registration_data["password"],
        fb_user_id="102525138920866",
    )
