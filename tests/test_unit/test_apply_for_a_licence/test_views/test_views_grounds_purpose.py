from apply_for_a_licence.choices import ProfessionalOrBusinessServicesChoices
from django.urls import reverse


class TestLicensingGroundsView:
    def test_legal_advisory_h1_header_form_kwargs(self, al_client):
        session = al_client.session
        session["professional_or_business_services"] = {
            "professional_or_business_service": [ProfessionalOrBusinessServicesChoices.legal_advisory.value]
        }
        session.save()

        response = al_client.get(reverse("licensing_grounds"))
        form = response.context["form"]
        assert (
            form.form_h1_header == "Which of these licensing grounds describes the purpose of the relevant activity "
            "for which the legal advice is being given?"
        )

    def test_normal_h1_header_form_kwargs(self, al_client):
        response = al_client.get(reverse("licensing_grounds"))
        form = response.context["form"]
        assert (
            form.form_h1_header
            == "Which of these licensing grounds describes your purpose for providing the sanctioned services?"
        )

    def test_audit_h1_header_form_kwargs(self, al_client):
        session = al_client.session
        session["professional_or_business_services"] = {
            "professional_or_business_service": [ProfessionalOrBusinessServicesChoices.auditing.value]
        }
        session.save()

        response = al_client.get(reverse("licensing_grounds"))
        form = response.context["form"]
        assert form.audit_service_selected


class TestLicensingGroundsLegalAdvisoryView:
    def test_form_h1_header(self, al_client):
        response = al_client.get(reverse("licensing_grounds_legal_advisory"))
        form = response.context["form"]
        assert (
            form.form_h1_header == "For the other services you want to provide (excluding legal advisory), "
            "which of these licensing grounds describes your purpose for providing them?"
        )
