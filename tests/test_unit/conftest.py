import pytest
from core.sites import SiteName
from django.conf import settings
from django.contrib.sites.models import Site


@pytest.fixture(autouse=True)
def django_sites_setup(db):
    """Create the sites for the apply-for-a-licence and view-a-licence domains if they don't already exist."""
    Site.objects.get_or_create(
        domain=settings.APPLY_FOR_A_LICENCE_DOMAIN,
        name=SiteName.apply_for_a_licence,
    )
    Site.objects.get_or_create(
        domain=settings.VIEW_A_LICENCE_DOMAIN,
        name=SiteName.view_a_licence,
    )
