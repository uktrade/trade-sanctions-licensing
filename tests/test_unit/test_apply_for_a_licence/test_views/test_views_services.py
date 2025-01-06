import pytest
from apply_for_a_licence.choices import (
    ProfessionalOrBusinessServicesChoices,
    TypeOfServicesChoices,
)
from django.urls import reverse


@pytest.mark.django_db
class TestProfessionalOrBusinessServicesView:
    def test_post(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("professional_or_business_services"),
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )
        assert response.status_code == 302
        assert response.url == reverse("service_activities")

    def test_changed_success_url(self, authenticated_al_client):
        authenticated_al_client.post(
            reverse("professional_or_business_services") + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )

        # duplicating the response so we're changing the value
        response = authenticated_al_client.post(
            reverse("professional_or_business_services") + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.advertising.value},
        )
        assert response.status_code == 302
        assert response.url == reverse("service_activities") + "?update=yes&redirect_to_url=check_your_answers"


class TestTypeOfServiceView:
    def test_get_success_url(self, al_client):
        response = al_client.post(
            reverse("type_of_service"),
            data={"type_of_service": TypeOfServicesChoices.interception_or_monitoring.value},
        )
        assert response.url == reverse("which_sanctions_regime")

        response = al_client.post(
            reverse("type_of_service"),
            data={"type_of_service": TypeOfServicesChoices.professional_and_business.value},
        )
        assert response.url == reverse("professional_or_business_services")

        response = al_client.post(
            reverse("type_of_service"),
            data={"type_of_service": TypeOfServicesChoices.ships_or_aircraft_related.value},
        )
        assert response.url == reverse("service_activities")

    def test_session_cleared_if_changed(self, al_client):
        session = al_client.session
        session["service_activities"] = {"key": "value"}
        session["purpose_of_provision"] = {"key": "value"}
        session.save()

        al_client.post(
            reverse("type_of_service") + "?redirect_to_url=check_your_answers",
            data={"type_of_service": TypeOfServicesChoices.interception_or_monitoring.value},
        )

        # duplicating the response as we're changing the value
        al_client.post(
            reverse("type_of_service") + "?redirect_to_url=check_your_answers",
            data={"type_of_service": TypeOfServicesChoices.mining_manufacturing_or_computer.value},
        )

        assert al_client.session["service_activities"] == {}
        assert al_client.session["purpose_of_provision"] == {}
