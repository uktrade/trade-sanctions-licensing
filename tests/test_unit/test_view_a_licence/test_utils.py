from django.test import override_settings
from django.urls import reverse
from view_a_licence.utils import (
    craft_view_a_licence_url,
    get_view_a_licence_application_url,
)


@override_settings(PROTOCOL="https://", VIEW_A_LICENCE_DOMAIN="view-a-licence.com")
def test_craft_view_a_licence_url():
    url = craft_view_a_licence_url("/view-application/123/")
    assert url == "https://view-a-licence.com/view-application/123/"


@override_settings(PROTOCOL="https://", VIEW_A_LICENCE_DOMAIN="view-a-licence.com")
def test_get_view_a_licence_application_url():
    url = get_view_a_licence_application_url("123")
    assert url == "https://view-a-licence.com/view/view-application/123/"


@override_settings(PROTOCOL="", VIEW_A_LICENCE_DOMAIN="")
def test_get_view_a_licence_application_url_matches_hardcoded_url():
    # checks that the hardcoded URL matches the expected URL
    actual_url = reverse("view_a_licence:view_application", kwargs={"reference": "123"})
    crafted_url = get_view_a_licence_application_url("123")
    assert crafted_url == actual_url
