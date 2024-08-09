import logging

from apply_for_a_licence.forms import forms_services as forms
from core.views.base_views import BaseFormView
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class TypeOfServiceView(BaseFormView):
    form_class = forms.TypeOfServiceForm
    redirect_after_post = False

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["type_of_service"]
        match answer:
            case "interception_or_monitoring":
                success_url = reverse("which_sanctions_regime")
            case "internet":
                success_url = reverse("which_sanctions_regime")
            case "professional_and_business":
                success_url = reverse("professional_or_business_services")
            case _:
                success_url = reverse("service_activities")
        return success_url


class ProfessionalOrBusinessServicesView(BaseFormView):
    form_class = forms.ProfessionalOrBusinessServicesForm
    success_url = reverse_lazy("service_activities")


class WhichSanctionsRegimeView(BaseFormView):
    form_class = forms.WhichSanctionsRegimeForm
    success_url = reverse_lazy("service_activities")


class ServiceActivitiesView(BaseFormView):
    form_class = forms.ServiceActivitiesForm
    success_url = reverse_lazy("where_is_the_recipient_located")
