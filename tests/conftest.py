import pytest
from apply_for_a_licence.choices import WhoDoYouWantTheLicenceToCoverChoices
from apply_for_a_licence.models import Individual, Licence
from core.sites import SiteName
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.test import Client, RequestFactory
from django.utils import timezone

from tests.factories import LicenceFactory, OrganisationFactory
from tests.helpers import get_test_client


@pytest.fixture()
def test_apply_user(db) -> User:
    user, _ = User.objects.get_or_create(
        username="urn:fdc:test_apply_user",
        defaults={
            "first_name": "Test",
            "last_name": "User",
            "email": "apply_test_user@example.com",
            "is_active": True,
            "is_staff": False,
            "password": "test",
        },
    )
    return user


@pytest.fixture()
def al_client(db) -> Client:
    al_site = Site.objects.get(name=SiteName.apply_for_a_licence)
    al_client = get_test_client(al_site.domain)

    # setting the last_activity key in the session to prevent the session from expiring
    session = al_client.session
    session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()
    session.save()
    return al_client


@pytest.fixture()
def authenticated_al_client(al_client, test_apply_user) -> Client:
    """Client used to access the apply-for-a-licence site.

    The test_apply_user user is logged in with this client.
    """
    al_client.force_login(test_apply_user, backend="authentication.backends.OneLoginBackend")
    return al_client


@pytest.fixture()
def authenticated_al_client_with_licence(authenticated_al_client, test_apply_user, licence_application) -> Client:
    """Client used to access the apply-for-a-licence site.

    The test_apply_user user is logged in with this client and a licence is created belonging to this user
    """
    session = authenticated_al_client.session
    licence_application.user = test_apply_user
    licence_application.save()
    session["licence_id"] = licence_application.id
    session.save()
    return authenticated_al_client


@pytest.fixture()
def vl_client(db) -> Client:
    """Client used to access the view-a-licence site.

    No user is logged in with this client.
    """
    vl_site = Site.objects.get(name=SiteName.view_a_licence)
    return get_test_client(vl_site.domain)


@pytest.fixture()
def staff_user(db):
    try:
        return User.objects.create_user(
            "staff",
            "staff@example.com",
            is_active=True,
            is_staff=True,
        )
    except IntegrityError:
        return User.objects.get(username="staff")


@pytest.fixture()
def vl_client_logged_in(vl_client, staff_user) -> Client:
    """Client used to access the view-a-licence site.

    The staff_user user is logged in with this client"""

    vl_client.force_login(staff_user)
    return vl_client


@pytest.fixture()
def request_object(authenticated_al_client: Client, test_apply_user: User):
    """Fixture to create a request object."""
    request_object = RequestFactory()
    request_object.session = authenticated_al_client.session
    request_object.method = "GET"
    request_object.user = test_apply_user
    request_object.GET = {}
    request_object.POST = {}
    request_object.META = {}
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
    return LicenceFactory(status="submitted")


@pytest.fixture()
def apply_rf(request_object):
    request_object.site = Site.objects.get(name=SiteName.apply_for_a_licence)
    return request_object


@pytest.fixture()
def viewer_rf(request_object):
    request_object.site = Site.objects.get(name=SiteName.view_a_licence)
    return request_object


@pytest.fixture()
def licence_application(authenticated_al_client, test_apply_user) -> Licence:
    licence_object = LicenceFactory(user=test_apply_user)
    session = authenticated_al_client.session
    session["licence_id"] = licence_object.id
    session.save()
    return licence_object


@pytest.fixture()
def individual_licence(authenticated_al_client, test_apply_user):
    licence_object = Licence.objects.create(
        user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value
    )

    session = authenticated_al_client.session
    session["licence_id"] = licence_object.id
    session.save()
    return licence_object


@pytest.fixture()
def yourself_licence(authenticated_al_client, test_apply_user):
    licence_object = Licence.objects.create(
        user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.myself.value
    )

    session = authenticated_al_client.session
    session["licence_id"] = licence_object.id
    session.save()
    return licence_object


@pytest.fixture()
def individual(individual_licence):
    individual = Individual.objects.create(
        licence=individual_licence,
    )
    return individual


@pytest.fixture()
def yourself(yourself_licence):
    yourself_licence.applicant_full_name = "Your Name"
    yourself = Individual.objects.create(
        licence=yourself_licence,
        first_name="Your",
        last_name="Name",
        is_applicant=True,
    )
    return yourself


@pytest.fixture()
def organisation(licence_application):
    organisation = OrganisationFactory(
        licence=licence_application,
    )
    return organisation


@pytest.fixture()
def recipient_organisation(organisation):
    organisation.type_of_relationship = "recipient"
    organisation.save()
    return organisation
