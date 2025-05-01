from apply_for_a_licence.choices import (
    LicensingGroundsChoices,
    ProfessionalOrBusinessServicesChoices,
)
from django.urls import reverse


class TestLicensingGroundsView:
    def test_legal_advisory_h1_header_form_kwargs(self, authenticated_al_client_with_licence, licence_application):
        licence_application.professional_or_business_services = [ProfessionalOrBusinessServicesChoices.legal_advisory.value]
        licence_application.save()

        response = authenticated_al_client_with_licence.get(
            reverse("licensing_grounds", kwargs={"licence_pk": licence_application.id})
        )
        form = response.context["form"]
        assert (
            form.form_h1_header == "Which of these licensing grounds describes the purpose of the relevant activity "
            "for which the legal advice is being given?"
        )

    def test_normal_h1_header_form_kwargs(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.get(
            reverse("licensing_grounds", kwargs={"licence_pk": licence_application.id})
        )
        form = response.context["form"]
        assert (
            form.form_h1_header
            == "Which of these licensing grounds describes your purpose for providing the sanctioned services?"
        )

    def test_get_success_url_legal_advisory(self, authenticated_al_client_with_licence, licence_application):
        licence_application.professional_or_business_services = [
            ProfessionalOrBusinessServicesChoices.legal_advisory.value,
            ProfessionalOrBusinessServicesChoices.auditing.value,
        ]
        licence_application.save()

        response = authenticated_al_client_with_licence.post(
            reverse("licensing_grounds", kwargs={"licence_pk": licence_application.id}),
            data={"licensing_grounds": LicensingGroundsChoices.safety.value},
        )
        assert response.url == reverse("licensing_grounds_legal_advisory", kwargs={"licence_pk": licence_application.id})

    def test_get_success_url_purpose_of_provision(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.post(
            reverse("licensing_grounds", kwargs={"licence_pk": licence_application.id}),
            data={"licensing_grounds": LicensingGroundsChoices.safety.value},
        )
        assert response.url == reverse("purpose_of_provision", kwargs={"licence_pk": licence_application.id})


class TestLicensingGroundsLegalAdvisoryView:
    def test_form_h1_header(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.get(
            reverse("licensing_grounds_legal_advisory", kwargs={"licence_pk": licence_application.id})
        )
        form = response.context["form"]
        assert (
            form.form_h1_header == "For the other services you want to provide (excluding legal advisory), "
            "which of these licensing grounds describes your purpose for providing them?"
        )

    def test_get_form_kwargs_update(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.get(
            reverse("licensing_grounds_legal_advisory", kwargs={"licence_pk": licence_application.id}) + "?update=yes"
        )
        form = response.context["form"]
        assert not form.is_bound

    def test_success_url(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.post(
            reverse("licensing_grounds_legal_advisory", kwargs={"licence_pk": licence_application.id}),
            data={"licensing_grounds_legal_advisory": LicensingGroundsChoices.safety.value},
        )
        assert response.url == reverse("purpose_of_provision", kwargs={"licence_pk": licence_application.id})


class TestPurposeOfProvisionView:
    def test_success_url(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.post(
            reverse("purpose_of_provision", kwargs={"licence_pk": licence_application.id}),
            data={"purpose_of_provision": "purpose"},
        )
        assert response.url == reverse("tasklist", kwargs={"licence_pk": licence_application.id})
