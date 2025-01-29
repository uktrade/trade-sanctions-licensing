import sys
from importlib import import_module, reload
from unittest.mock import MagicMock

from django.conf import settings
from django.http import HttpResponse
from django.test import Client
from django.urls import clear_url_caches


def get_test_client(server_name: str) -> Client:
    """Create a test client for a particular site.

    :param server_name: Domain to link to the correct site.

    """
    client = Client(SERVER_NAME=server_name)

    return client


def get_response_content(response: HttpResponse) -> str:
    """Get the body of a response as a string.

    :param response: The response to get the body of.

    """
    return response.content.decode("utf-8")


class InfiniteDict(MagicMock):
    """A dictionary that can be infinitely nested, used in tests to mock massive session objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.internal_dict = {}

    def __getitem__(self, item):
        if item not in self.internal_dict:
            return "INFINITE DICT"
        else:
            return self.internal_dict[item]

    def __setitem__(self, key, value):
        self.internal_dict[key] = value


def reload_urlconf():
    clear_url_caches()
    if settings.ROOT_URLCONF in sys.modules:
        reload(sys.modules[settings.ROOT_URLCONF])
    return import_module(settings.ROOT_URLCONF)
