from apply_for_a_licence.choices import (
    TypeOfRelationshipChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
)
from django.urls import reverse

from tests.factories import LicenceFactory, OrganisationFactory


def test_context_data(vl_client_logged_in, licence):
    licence.assign_reference()
    licence.who_do_you_want_the_licence_to_cover = WhoDoYouWantTheLicenceToCoverChoices.individual
    licence.save()
    org = OrganisationFactory.create(
        licence=licence,
        type_of_relationship=TypeOfRelationshipChoices.named_individuals,
    )
    response = vl_client_logged_in.get(reverse("view_a_licence:view_application", kwargs={"reference": licence.reference}))
    assert response.context["business_individuals_work_for"] == org


def test_cant_view_draft_licence_application(vl_client_logged_in):
    draft_licence = LicenceFactory(status="draft")
    response = vl_client_logged_in.get(reverse("view_a_licence:view_application", kwargs={"reference": draft_licence.reference}))
    assert response.status_code == 404
