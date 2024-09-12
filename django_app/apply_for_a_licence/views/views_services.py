import logging
import urllib.parse

from apply_for_a_licence.forms import forms_services as forms
from core.views.base_views import BaseFormView
from django.urls import reverse

logger = logging.getLogger(__name__)


class TypeOfServiceView(BaseFormView):
    form_class = forms.TypeOfServiceForm

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["type_of_service"]
        print(self.form.is_valid())
        match answer:
            case "interception_or_monitoring":
                success_url = reverse("which_sanctions_regime")
                if self.changed_fields.get("type_of_service"):
                    self.redirect_after_post = False
            case "professional_and_business":
                success_url = reverse("professional_or_business_services")
                if self.changed_fields.get("type_of_service"):
                    self.redirect_after_post = False
            case _:
                success_url = reverse("service_activities")

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        # changed from Professional or Business Services to other service
        if self.changed_fields.get("type_of_service") == "professional_and_business":
            # delete form data for professional business services and licensing grounds
            self.request.session["professional_or_business_services"] = {}
            self.request.session["licensing_grounds"] = {}
            self.redirect_after_post = False

        # changed from Interception or Monitoring to other service
        if self.changed_fields.get("type_of_service") == "interception_or_monitoring":
            self.request.session["which_sanctions_regime"] = {}

        return success_url


class ProfessionalOrBusinessServicesView(BaseFormView):
    form_class = forms.ProfessionalOrBusinessServicesForm

    def get_success_url(self) -> str:
        success_url = reverse("service_activities")

        if self.request.GET.get("change", None) == "yes":
            self.redirect_after_post = False

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        return success_url


class WhichSanctionsRegimeView(BaseFormView):
    form_class = forms.WhichSanctionsRegimeForm

    def get_success_url(self) -> str:
        success_url = reverse("service_activities")

        if self.request.GET.get("change", None) == "yes":
            self.redirect_after_post = False

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        return success_url


class ServiceActivitiesView(BaseFormView):
    form_class = forms.ServiceActivitiesForm

    def get_success_url(self) -> str:
        success_url = reverse("where_is_the_recipient_located")

        if self.request.GET.get("change", None) == "yes":
            self.redirect_after_post = False
            success_url = reverse("purpose_of_provision")

        return success_url
