import logging
import uuid

from apply_for_a_licence.choices import TypeOfServicesChoices
from apply_for_a_licence.forms import forms_services as forms
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class TypeOfServiceView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.TypeOfServiceForm

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["type_of_service"]
        match answer:
            case "interception_or_monitoring":
                success_url = reverse("which_sanctions_regime")
            case "professional_and_business":
                success_url = reverse("professional_or_business_services")
            case _:
                success_url = reverse("service_activities")

        return success_url

    def save_form(self, form):
        licence = super().save_form(form)
        if form.has_field_changed("type_of_service"):
            self.redirect_after_post = False
        return licence


class ProfessionalOrBusinessServicesView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.ProfessionalOrBusinessServicesForm
    success_url = reverse_lazy("service_activities")

    def add_query_parameters_to_url(self, success_url: str) -> str:
        success_url = super().add_query_parameters_to_url(success_url)
        # We need separate logic here if coming from CYA as we
        # only want to go through the full update flow for pbs if it's actually changed.
        if self.form.has_field_changed("professional_or_business_services") and "redirect_to_url" in self.request.GET:
            if "?" in success_url:
                success_url += "&"
            else:
                success_url += "?"

            success_url += "update=yes"

        return success_url

    def form_valid(self, form):
        if form.has_field_changed("professional_or_business_services"):
            self.redirect_after_post = False
        return super().form_valid(form)


class WhichSanctionsRegimeView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.WhichSanctionsRegimeForm
    success_url = reverse_lazy("service_activities")

    @property
    def redirect_after_post(self) -> bool:
        if self.request.GET.get("update", None) == "yes":
            return False
        return True


class ServiceActivitiesView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.ServiceActivitiesForm

    @property
    def redirect_after_post(self) -> bool:
        if self.update:
            return False
        return True

    def get_success_url(self) -> str:
        success_url = reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": uuid.uuid4()})

        if self.update:
            success_url = reverse("purpose_of_provision")
            if self.form.instance.professional_or_business_services == TypeOfServicesChoices.professional_and_business.value:
                success_url = reverse("licensing_grounds")

        return success_url
