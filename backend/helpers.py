from django.conf import settings


def get_domain():
    return settings.BASE_URL.split("/")[1].split(":")[0]
