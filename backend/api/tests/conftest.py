from django.test import Client

import pytest


@pytest.fixture
def client():
    return Client()
