import logging

from apply_for_a_licence.choices import ProfessionalOrBusinessServicesChoices
from apply_for_a_licence.forms import forms_grounds_purpose as forms
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class LicensingGroundsView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.LicensingGroundsForm
    redirect_after_post = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if (
            self.licence_object.professional_or_business_services
            and ProfessionalOrBusinessServicesChoices.legal_advisory.value
            in self.licence_object.professional_or_business_services
        ):
            kwargs["form_h1_header"] = (
                "Which of these licensing grounds describes the purpose of the relevant activity for "
                "which the legal advice is being given?"
            )
        else:
            kwargs["form_h1_header"] = (
                "Which of these licensing grounds describes your purpose for providing the sanctioned services?"
            )

        return kwargs

    def get_success_url(self) -> str:
        licence = self.licence_object
        if (
            ProfessionalOrBusinessServicesChoices.legal_advisory.value in licence.professional_or_business_services
            and len(licence.professional_or_business_services) > 1
        ):
            # the user has selected 'Legal advisory' as well as other services, redirect them to the legal advisory page
            success_url = reverse("licensing_grounds_legal_advisory")
        else:
            # delete form data for legal advisory grounds
            licence.licensing_grounds_legal_advisory = None
            licence.save()
            success_url = reverse("purpose_of_provision")

        return success_url


class LicensingGroundsLegalAdvisoryView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.LicensingGroundsLegalAdvisoryForm
    success_url = reverse_lazy("purpose_of_provision")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["form_h1_header"] = (
            "For the other services you want to provide (excluding legal advisory), which of these "
            "licensing grounds describes your purpose for providing them?"
        )
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.method == "GET" and self.update:
            # clear the form data if the user is coming from the CYA page
            form.is_bound = False
        return form


class PurposeOfProvisionView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.PurposeOfProvisionForm
    success_url = reverse_lazy("upload_documents")
