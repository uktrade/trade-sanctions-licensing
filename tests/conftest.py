import pytest
from core.sites import SiteName
from django.contrib.sites.models import Site
from django.test import Client, RequestFactory

from tests.factories import RegimeFactory
from tests.helpers import get_test_client


@pytest.fixture()
def al_client(db) -> Client:
    """Client used to access the apply-for-a-license site.

    No user is logged in with this client.
    """
    al_site = Site.objects.get(name=SiteName.apply_for_a_licence)
    return get_test_client(al_site.domain)


@pytest.fixture()
def vl_client(db) -> Client:
    """Client used to access the view-a-license site.

    No user is logged in with this client.
    """
    vl_site = Site.objects.get(name=SiteName.view_a_licence)
    return get_test_client(vl_site.domain)


@pytest.fixture()
def regime_object(db):
    """Fixture to create a Regime object."""
    return RegimeFactory()


@pytest.fixture()
def request_object(al_client: Client, method: str = "GET"):
    """Fixture to create a request object."""
    request_object = RequestFactory()
    request_object.session = al_client.session
    request_object.method = method
    request_object.GET = {}
    request_object.POST = {}
    return request_object
