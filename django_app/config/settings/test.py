from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.dummy import DummyCache

from .base import *  # noqa

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = True

BASE_FRONTEND_TESTING_URL = "http://apply-for-a-licence:8000"

ENVIRONMENT = "test"

# we don't want to connect to ClamAV in testing, redefine and remove from list
FILE_UPLOAD_HANDLERS = ("core.custom_upload_handler.CustomFileUploadHandler",)  # Order is important


# don't use redis when testing
class TestingCache(DummyCache):
    """A dummy cache that implements the same interface as the django-redis cache."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dict_cache = {}

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        if key in self.dict_cache:
            return False
        self.dict_cache[key] = value
        return True

    def get(self, key, *args, **kwargs):
        return self.dict_cache.get(key)

    def set(self, key, value, **kwargs):
        self.dict_cache[key] = value

    def iter_keys(self, *args, search="", **kwargs):
        for key in self.dict_cache.keys():
            if search in key:
                yield key

    def clear(self):
        self.dict_cache = {}


CACHES = {"default": {"BACKEND": "config.settings.test.TestingCache"}}
