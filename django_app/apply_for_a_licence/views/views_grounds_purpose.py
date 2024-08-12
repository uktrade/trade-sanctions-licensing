import logging

from apply_for_a_licence.forms import forms_grounds_purpose as forms
from core.views.base_views import BaseFormView
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class LicensingGroundsView(BaseFormView):
    form_class = forms.LicensingGroundsForm
    success_url = reverse_lazy("purpose_of_provision")

    def get_success_url(self) -> str:

        if professional_or_business_service := self.request.session.get("ProfessionalOrBusinessServicesView", False):
            if professional_or_business_service.get("professional_or_business_service") == "legal_advisory":
                return reverse("licensing_grounds_legal_advisory")
        return reverse("purpose_of_provision")


class LicensingGroundsLegalAdvisoryView(BaseFormView):
    form_class = forms.LicensingGroundsForm
    success_url = reverse_lazy("upload_documents")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["legal_advisory"] = True
        return kwargs


class PurposeOfProvisionView(BaseFormView):
    form_class = forms.PurposeOfProvisionForm
    success_url = reverse_lazy("upload_documents")
