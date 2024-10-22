import pytest
from apply_for_a_licence.choices import ProfessionalOrBusinessServicesChoices
from django.urls import reverse


@pytest.mark.django_db
class TestProfessionalOrBusinessServicesView:
    def test_post(self, al_client):
        response = al_client.post(
            reverse("professional_or_business_services"),
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )
        assert response.status_code == 302
        assert response.url == reverse("service_activities")

    def test_changed_success_url(self, al_client):
        al_client.post(
            reverse("professional_or_business_services") + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )

        # duplicating the response so we're changing the value
        response = al_client.post(
            reverse("professional_or_business_services") + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.advertising.value},
        )
        assert response.status_code == 302
        assert response.url == reverse("service_activities") + "?update=yes&redirect_to_url=check_your_answers"
