import logging

from apply_for_a_licence.choices import TypeOfServicesChoices
from apply_for_a_licence.forms import forms_services as forms
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.urls import reverse

logger = logging.getLogger(__name__)


class TypeOfServiceView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.TypeOfServiceForm
    redirect_with_query_parameters = True

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["type_of_service"]
        match answer:
            case "interception_or_monitoring":
                success_url = reverse("which_sanctions_regime", kwargs={"licence_pk": self.kwargs["licence_pk"]})
            case "professional_and_business":
                success_url = reverse("professional_or_business_services", kwargs={"licence_pk": self.kwargs["licence_pk"]})
            case _:
                success_url = reverse("service_activities", kwargs={"licence_pk": self.kwargs["licence_pk"]})

        return success_url

    def save_form(self, form):
        licence = super().save_form(form)
        if form.has_field_changed("type_of_service"):
            self.redirect_after_post = False
        return licence


class ProfessionalOrBusinessServicesView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.ProfessionalOrBusinessServicesForm
    redirect_with_query_parameters = True

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

    def get_success_url(self):
        success_url = reverse("service_activities", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class WhichSanctionsRegimeView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.WhichSanctionsRegimeForm

    @property
    def redirect_after_post(self) -> bool:
        if self.request.GET.get("update", None) == "yes":
            return False
        return True

    def get_success_url(self):
        success_url = reverse("service_activities", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class ServiceActivitiesView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.ServiceActivitiesForm
    redirect_with_query_parameters = True

    @property
    def redirect_after_post(self) -> bool:
        if self.update:
            return False
        return True

    def get_success_url(self) -> str:
        success_url = reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})

        if self.update:
            success_url = reverse("purpose_of_provision", kwargs={"licence_pk": self.kwargs["licence_pk"]})
            if self.form.instance.type_of_service == TypeOfServicesChoices.professional_and_business.value:
                success_url = reverse("licensing_grounds", kwargs={"licence_pk": self.kwargs["licence_pk"]})

        return success_url
