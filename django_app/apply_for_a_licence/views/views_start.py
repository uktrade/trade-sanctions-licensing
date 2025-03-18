import logging

from apply_for_a_licence.forms import forms_start as forms
from core.decorators import reset_last_activity_session_timestamp
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


@method_decorator(reset_last_activity_session_timestamp, name="dispatch")
class SubmitterReferenceView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.SubmitterReferenceForm

    @property
    def object(self) -> None:
        """This is the first step in the journey, so there is no object to retrieve."""
        return None

    def save_form(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        self.request.session["licence_id"] = instance.id
        return instance

    def get_success_url(self):
        success_url = reverse_lazy("start", kwargs={"pk": self.instance.pk})
        return success_url


@method_decorator(reset_last_activity_session_timestamp, name="dispatch")
class StartView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.StartForm
    success_url = reverse_lazy("tasklist")


class ThirdPartyView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.ThirdPartyForm
    success_url = reverse_lazy("your_details")


class YourDetailsView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.YourDetailsForm
    success_url = reverse_lazy("tasklist")
