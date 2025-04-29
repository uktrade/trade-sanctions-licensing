import pytest
from apply_for_a_licence.choices import (
    ProfessionalOrBusinessServicesChoices,
    TypeOfServicesChoices,
)
from apply_for_a_licence.views.views_services import (
    ServiceActivitiesView,
    WhichSanctionsRegimeView,
)
from django.test import RequestFactory
from django.urls import reverse


@pytest.mark.django_db
class TestProfessionalOrBusinessServicesView:
    def test_post(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services", kwargs={"licence_pk": licence_application.id}),
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )
        assert response.status_code == 302
        assert response.url == reverse("service_activities", kwargs={"licence_pk": licence_application.id})

    def test_changed_success_url(self, authenticated_al_client_with_licence, licence_application):
        authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services", kwargs={"licence_pk": licence_application.id})
            + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )

        # duplicating the response so we're changing the value
        response = authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services", kwargs={"licence_pk": licence_application.id})
            + "?redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.advertising.value},
        )
        assert response.status_code == 302
        assert (
            response.url
            == reverse("service_activities", kwargs={"licence_pk": licence_application.id})
            + "?redirect_to_url=check_your_answers&update=yes"
        )

    def test_add_query_parameters(self, authenticated_al_client_with_licence, licence_application):
        authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services", kwargs={"licence_pk": licence_application.id})
            + "?change=yes&redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.accounting.value},
        )

        # duplicating the response so we're changing the value
        response = authenticated_al_client_with_licence.post(
            reverse("professional_or_business_services", kwargs={"licence_pk": licence_application.id})
            + "?change=yes&redirect_to_url=check_your_answers",
            data={"professional_or_business_services": ProfessionalOrBusinessServicesChoices.advertising.value},
        )
        assert response.status_code == 302
        assert (
            response.url
            == reverse("service_activities", kwargs={"licence_pk": licence_application.id})
            + "?change=yes&redirect_to_url=check_your_answers&update=yes"
        )


class TestTypeOfServiceView:
    def test_get_success_url(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.post(
            reverse("type_of_service", kwargs={"licence_pk": licence_application.id}),
            data={"type_of_service": TypeOfServicesChoices.interception_or_monitoring.value},
        )
        assert response.url == reverse("which_sanctions_regime", kwargs={"licence_pk": licence_application.id})

        response = authenticated_al_client_with_licence.post(
            reverse("type_of_service", kwargs={"licence_pk": licence_application.id}),
            data={"type_of_service": TypeOfServicesChoices.professional_and_business.value},
        )
        assert response.url == reverse("professional_or_business_services", kwargs={"licence_pk": licence_application.id})

        response = authenticated_al_client_with_licence.post(
            reverse("type_of_service", kwargs={"licence_pk": licence_application.id}),
            data={"type_of_service": TypeOfServicesChoices.ships_or_aircraft_related.value},
        )
        assert response.url == reverse("service_activities", kwargs={"licence_pk": licence_application.id})

    def test_session_cleared_if_changed(self, authenticated_al_client_with_licence, licence_application):
        licence_application.service_activities = ["test"]
        licence_application.purpose_of_provision = "test"
        licence_application.save()

        authenticated_al_client_with_licence.post(
            reverse("type_of_service", kwargs={"licence_pk": licence_application.id}) + "?redirect_to_url=check_your_answers",
            data={"type_of_service": TypeOfServicesChoices.interception_or_monitoring.value},
        )

        # duplicating the response as we're changing the value
        authenticated_al_client_with_licence.post(
            reverse("type_of_service", kwargs={"licence_pk": licence_application.id}) + "?redirect_to_url=check_your_answers",
            data={"type_of_service": TypeOfServicesChoices.mining_manufacturing_or_computer.value},
        )
        licence_application.refresh_from_db()
        assert not licence_application.service_activities
        assert not licence_application.purpose_of_provision


class TestWhichSanctionsRegimeView:
    def test_redirect_after_post(self, licence_application):
        request = RequestFactory().get(reverse("which_sanctions_regime", kwargs={"licence_pk": licence_application.id}))
        view = WhichSanctionsRegimeView()
        view.setup(request)
        assert view.redirect_after_post
        view = WhichSanctionsRegimeView(update=True)
        request.GET = {"update": "yes"}
        view.setup(request)
        assert not view.redirect_after_post


class TestServiceActivitiesView:
    def test_get_success_url(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.post(
            reverse("service_activities", kwargs={"licence_pk": licence_application.id}),
            data={"service_activities": "activities"},
        )

        assert response.url == reverse("tasklist", kwargs={"licence_pk": licence_application.id})

    def test_get_update_success_url(self, authenticated_al_client, licence_application, request_object):
        request_object.GET = {"change": "yes"}
        response = authenticated_al_client.post(
            reverse("service_activities", kwargs={"licence_pk": licence_application.id}) + "?update=yes",
            data={"service_activities": "activities"},
        )

        assert response.url == reverse("purpose_of_provision", kwargs={"licence_pk": licence_application.id}) + "?update=yes"

    def test_get_pbs_success_url(self, authenticated_al_client_with_licence, licence_application, request_object):
        request_object.GET = {"change": "yes"}
        licence_application.type_of_service = TypeOfServicesChoices.professional_and_business.value
        licence_application.save()
        response = authenticated_al_client_with_licence.post(
            reverse("service_activities", kwargs={"licence_pk": licence_application.id}) + "?update=yes",
            data={"service_activities": "activities"},
        )

        assert response.url == reverse("licensing_grounds", kwargs={"licence_pk": licence_application.id}) + "?update=yes"

    def test_redirect_after_post(self, licence_application):
        request = RequestFactory().get(reverse("service_activities", kwargs={"licence_pk": licence_application.id}))
        view = ServiceActivitiesView(update=False)
        view.setup(request)
        assert view.redirect_after_post
        view = ServiceActivitiesView(update=True)
        view.setup(request)
        assert not view.redirect_after_post
