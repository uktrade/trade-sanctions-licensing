import pytest
from django.conf import settings

from tests.test_frontend.conftest import PlaywrightTestBase as BasePlaywrightTestBase


class PlaywrightTestBase(BasePlaywrightTestBase):
    @property
    def base_host(self) -> str:
        return settings.VIEW_A_LICENCE_DOMAIN.split(":")[0]


@pytest.fixture(autouse=True, scope="function")
def bypass_login(monkeypatch, staff_user):
    def patched_get_user(request):
        return staff_user

    monkeypatch.setattr("django.contrib.auth.get_user", patched_get_user)

    yield
