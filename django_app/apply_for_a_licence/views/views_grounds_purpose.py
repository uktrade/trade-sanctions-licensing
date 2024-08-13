import logging

from apply_for_a_licence.choices import ProfessionalOrBusinessServicesChoices
from apply_for_a_licence.forms import forms_grounds_purpose as forms
from apply_for_a_licence.utils import get_cleaned_data_for_step
from core.views.base_views import BaseFormView
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class LicensingGroundsView(BaseFormView):
    form_class = forms.LicensingGroundsForm
    success_url = reverse_lazy("purpose_of_provision")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.professional_or_business_services_data = get_cleaned_data_for_step(
            self.request, "professional_or_business_services"
        ).get("professional_or_business_service", [])
        if ProfessionalOrBusinessServicesChoices.legal_advisory.value in self.professional_or_business_services_data:
            kwargs["form_h1_header"] = (
                "Which of these licensing grounds describes the purpose of the relevant activity for "
                "which the legal advice is being given?"
            )
        else:
            kwargs["form_h1_header"] = (
                "Which of these licensing grounds describes your purpose for providing the sanctioned services?"
            )

        if ProfessionalOrBusinessServicesChoices.auditing in self.professional_or_business_services_data:
            kwargs["audit_service_selected"] = True

        return kwargs

    def get_success_url(self) -> str:
        if (
            ProfessionalOrBusinessServicesChoices.legal_advisory.value in self.professional_or_business_services_data
            and len(self.professional_or_business_services_data) > 1
        ):
            # the user has selected 'Legal advisory' as well as other services, redirect them to the legal advisory page
            return reverse("licensing_grounds_legal_advisory")
        else:
            return reverse("purpose_of_provision")


class LicensingGroundsLegalAdvisoryView(BaseFormView):
    form_class = forms.LicensingGroundsForm
    success_url = reverse_lazy("purpose_of_provision")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["form_h1_header"] = (
            "For the other services you want to provide (excluding legal advisory), which of these "
            "licensing grounds describes your purpose for providing them?"
        )
        return kwargs


class PurposeOfProvisionView(BaseFormView):
    form_class = forms.PurposeOfProvisionForm
    success_url = reverse_lazy("upload_documents")
