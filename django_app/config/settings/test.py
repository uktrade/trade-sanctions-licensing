from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.dummy import DummyCache
from django.forms import Form
from django.http import HttpResponse

from .local import *  # noqa

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = env.headless

SAVE_VIDEOS = env.save_videos

ENVIRONMENT = "test"

INCLUDE_PRIVATE_URLS = True

# we don't want to connect to ClamAV in testing, redefine and remove from list
FILE_UPLOAD_HANDLERS = ("core.custom_upload_handler.CustomFileUploadHandler",)  # type: ignore[assignment]


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


def test_request_verify_code(self, form: Form) -> HttpResponse:
    """Monkey-patching the form_valid of the email address code view to always use the same verify code for testing."""

    from apply_for_a_licence.models import UserEmailVerification
    from apply_for_a_licence.views.views_start import WhatIsYouEmailAddressView
    from django.contrib.sessions.models import Session

    verify_code = "012345"
    user_session = Session.objects.get(session_key=self.request.session.session_key)
    UserEmailVerification.objects.create(
        user_session=user_session,
        email_verification_code=verify_code,
    )

    return super(WhatIsYouEmailAddressView, self).form_valid(form)
