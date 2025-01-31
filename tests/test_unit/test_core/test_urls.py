import pytest
from apply_for_a_licence.choices import WhoDoYouWantTheLicenceToCoverChoices
from django.test import override_settings
from django.urls import reverse

from tests.factories import LicenceFactory
from tests.helpers import reload_urlconf


@pytest.fixture(autouse=True, scope="function")
def reload_after_test_runs():
    yield
    reload_urlconf()


def test_private_urls_false(settings, authenticated_al_client):
    settings.INCLUDE_PRIVATE_URLS = False
    reload_urlconf()
    assert not settings.INCLUDE_PRIVATE_URLS
    licence = LicenceFactory()

    # assert can access apply urls
    response = authenticated_al_client.post(
        reverse("start", kwargs={"pk": licence.id}),
        data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value},
    )

    assert response.status_code == 302
    assert "your-name-nationality-location" in response.url

    # assert view urls return 404 not found
    response = authenticated_al_client.get("/view/")
    assert response.status_code == 404


@override_settings(INCLUDE_PRIVATE_URLS=True)
def test_private_urls_true(settings, authenticated_al_client):
    reload_urlconf()
    assert settings.INCLUDE_PRIVATE_URLS
    licence = LicenceFactory()

    # assert can access apply urls
    response = authenticated_al_client.post(
        reverse("start", kwargs={"pk": licence.id}),
        data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value},
    )

    assert response.status_code == 302
    assert "your-name-nationality-location" in response.url

    # assert view urls return 403 forbidden
    response = authenticated_al_client.get("/view/")
    assert response.status_code == 403


@override_settings(SHOW_ADMIN_PANEL=False)
def test_admin_panel_hidden_debug_false(settings, al_client):
    reload_urlconf()
    assert settings.INCLUDE_PRIVATE_URLS
    response = al_client.get("/admin/")
    assert response.status_code == 404


@override_settings(SHOW_ADMIN_PANEL=True)
def test_admin_panel_visible(settings, al_client):
    reload_urlconf()
    assert settings.INCLUDE_PRIVATE_URLS
    response = al_client.get("/admin/")
    assert response.status_code == 302
