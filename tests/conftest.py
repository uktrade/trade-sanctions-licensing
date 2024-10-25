import pytest
from core.sites import SiteName
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import Client, RequestFactory

from tests.factories import LicenceFactory
from tests.helpers import get_test_client


@pytest.fixture()
def al_client(db) -> Client:
    """Client used to access the apply-for-a-licence site.

    No user is logged in with this client.
    """
    al_site = Site.objects.get(name=SiteName.apply_for_a_licence)
    return get_test_client(al_site.domain)


@pytest.fixture()
def vl_client(db) -> Client:
    """Client used to access the view-a-licence site.

    No user is logged in with this client.
    """
    vl_site = Site.objects.get(name=SiteName.view_a_licence)
    return get_test_client(vl_site.domain)


@pytest.fixture()
def staff_user(db):
    return User.objects.create_user(
        "staff",
        "staff@example.com",
        is_active=True,
        is_staff=True,
    )


@pytest.fixture()
def vl_client_logged_in(vl_client, staff_user) -> Client:
    """Client used to access the view-a-licence site.

    A user is logged in with this client"""

    vl_client.force_login(staff_user)
    return vl_client


@pytest.fixture()
def request_object(al_client: Client):
    """Fixture to create a request object."""
    request_object = RequestFactory()
    request_object.session = al_client.session
    request_object.method = "GET"
    request_object.GET = {}
    request_object.POST = {}
    return request_object


@pytest.fixture()
def post_request_object(request_object):
    request_object.method = "POST"
    request_object.FILES = {}
    return request_object


@pytest.fixture()
def licence_request_object(request_object):
    steps = [
        "start",
        "is_the_business_registered_with_companies_house",
        "are_you_third_party",
        "add_yourself_address",
        "do_you_know_the_registered_company_number",
    ]
    for step in steps:
        request_object.session[step] = {}

    return request_object


@pytest.fixture()
def licence():
    return LicenceFactory()
