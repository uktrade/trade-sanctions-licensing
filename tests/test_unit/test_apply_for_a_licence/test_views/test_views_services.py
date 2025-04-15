import pytest
from apply_for_a_licence.choices import (
    ProfessionalOrBusinessServicesChoices,
    TypeOfServicesChoices,
)
from django.urls import reverse


@pytest.mark.django_db
class TestProfessionalOrBusinessServicesView:
    def test_post(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services"),
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )
        assert response.status_code == 302
        assert response.url == reverse("service_activities")

    def test_changed_success_url(self, authenticated_al_client_with_licence):
        authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services") + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )

        # duplicating the response so we're changing the value
        response = authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services") + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.advertising.value},
        )
        assert response.status_code == 302
        assert response.url == reverse("service_activities") + "?redirect_to_url=check_your_answers&update=yes"


class TestTypeOfServiceView:
    def test_get_success_url(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.post(
            reverse("type_of_service"),
            data={"type_of_service": TypeOfServicesChoices.interception_or_monitoring.value},
        )
        assert response.url == reverse("which_sanctions_regime")

        response = authenticated_al_client_with_licence.post(
            reverse("type_of_service"),
            data={"type_of_service": TypeOfServicesChoices.professional_and_business.value},
        )
        assert response.url == reverse("professional_or_business_services")

        response = authenticated_al_client_with_licence.post(
            reverse("type_of_service"),
            data={"type_of_service": TypeOfServicesChoices.ships_or_aircraft_related.value},
        )
        assert response.url == reverse("service_activities")

    def test_session_cleared_if_changed(self, authenticated_al_client_with_licence, licence_application):
        licence_application.service_activities = ["test"]
        licence_application.purpose_of_provision = "test"
        licence_application.save()

        authenticated_al_client_with_licence.post(
            reverse("type_of_service") + "?redirect_to_url=check_your_answers",
            data={"type_of_service": TypeOfServicesChoices.interception_or_monitoring.value},
        )

        # duplicating the response as we're changing the value
        authenticated_al_client_with_licence.post(
            reverse("type_of_service") + "?redirect_to_url=check_your_answers",
            data={"type_of_service": TypeOfServicesChoices.mining_manufacturing_or_computer.value},
        )
        licence_application.refresh_from_db()
        assert not licence_application.service_activities
        assert not licence_application.purpose_of_provision


class TestServiceActivitiesView:
    def test_get_success_url(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.post(
            reverse("service_activities"),
            data={"service_activities": "activities"},
        )

        assert response.url == reverse("tasklist")

    def test_get_update_success_url(self, authenticated_al_client, request_object):
        request_object.GET = {"change": "yes"}
        response = authenticated_al_client.post(
            reverse("service_activities") + "?update=yes", data={"service_activities": "activities"}
        )

        assert response.url == reverse("purpose_of_provision") + "?update=yes"

    def test_get_pbs_success_url(self, authenticated_al_client_with_licence, licence_application, request_object):
        request_object.GET = {"change": "yes"}
        licence_application.type_of_service = TypeOfServicesChoices.professional_and_business.value
        response = authenticated_al_client_with_licence.post(
            reverse("service_activities") + "?update=yes", data={"service_activities": "activities"}
        )

        assert response.url == reverse("purpose_of_provision") + "?update=yes"
