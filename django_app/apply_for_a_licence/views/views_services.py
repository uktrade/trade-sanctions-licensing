import logging
import urllib.parse

from apply_for_a_licence.choices import TypeOfServicesChoices
from apply_for_a_licence.forms import forms_services as forms
from core.views.base_views import BaseFormView
from django.urls import reverse

logger = logging.getLogger(__name__)


class TypeOfServiceView(BaseFormView):
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

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        if type_of_service := self.changed_fields.get("type_of_service", False):
            self.redirect_after_post = False

            # changed from Professional or Business Services to other service
            if type_of_service == "professional_and_business":
                # delete form data for professional business services and licensing grounds
                self.request.session["professional_or_business_services"] = {}
                self.request.session["licensing_grounds"] = {}

            # changed from Interception or Monitoring to other service
            if type_of_service == "interception_or_monitoring":
                self.request.session["which_sanctions_regime"] = {}

        return success_url


class ProfessionalOrBusinessServicesView(BaseFormView):
    form_class = forms.ProfessionalOrBusinessServicesForm

    def get_success_url(self) -> str:
        success_url = reverse("service_activities")
        url_params = ""

        if self.request.GET.get("update", None) == "yes":
            self.redirect_after_post = False

        # We need separate logic here as only want to go through the full update flow for pbs if it's actually changed.
        if self.changed_fields.get("professional_or_business_service", False):
            self.redirect_after_post = False
            url_params = "update=yes"

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + url_params + "&" + get_parameters
        else:
            success_url += "?" + url_params
        return success_url


class WhichSanctionsRegimeView(BaseFormView):
    form_class = forms.WhichSanctionsRegimeForm

    def get_success_url(self) -> str:
        success_url = reverse("service_activities")

        if self.request.GET.get("update", None) == "yes":
            self.redirect_after_post = False

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        return success_url


class ServiceActivitiesView(BaseFormView):
    form_class = forms.ServiceActivitiesForm

    def get_success_url(self) -> str:
        success_url = reverse("where_is_the_recipient_located")

        if self.request.GET.get("update", None) == "yes":
            self.redirect_after_post = False
            success_url = reverse("purpose_of_provision")
            # todo: use get_cleaned_data_for_step method here - form was invalid so wasn't working
            if professional_or_business_services := (self.request.session.get("type_of_service", {})):
                if (
                    professional_or_business_services.get("type_of_service", False)
                    == TypeOfServicesChoices.professional_and_business.value
                ):
                    success_url = reverse("licensing_grounds")

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        return success_url
