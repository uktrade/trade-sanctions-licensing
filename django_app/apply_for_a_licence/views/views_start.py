import logging
import uuid

from apply_for_a_licence.forms import forms_start as forms
from apply_for_a_licence.models import Licence
from core.utils import update_last_activity_session_timestamp
from core.views.base_views import BaseFormView, BaseLicenceFormView
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class SubmitterReferenceView(BaseFormView):
    form_class = forms.SubmitterReferenceForm

    def dispatch(self, request, *args, **kwargs):
        # refresh the session expiry timestamp. This is the start of the session
        update_last_activity_session_timestamp(request)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        success_url = reverse_lazy("start", kwargs={"pk": self.instance.pk})
        return success_url


class StartView(BaseFormView):
    form_class = forms.StartForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        licence_id = self.kwargs.get("pk")
        instance = Licence.objects.get(pk=licence_id)
        kwargs["instance"] = instance
        return kwargs

    def get_success_url(self) -> str | None:
        answer = self.form.cleaned_data["who_do_you_want_the_licence_to_cover"]
        if answer in ["business", "individual"]:
            return reverse("are_you_third_party")
        elif answer == "myself":
            return reverse("add_yourself", kwargs={"yourself_uuid": str(uuid.uuid4())})
        return None


class ThirdPartyView(BaseLicenceFormView):
    form_class = forms.ThirdPartyForm
    success_url = reverse_lazy("your_details")

    def get_success_url(self):
        if not self.form.cleaned_data["is_third_party"]:
            if self.instance.who_do_you_want_the_licence_to_cover == "business":
                return reverse("is_the_business_registered_with_companies_house", kwargs={"business_uuid": str(uuid.uuid4())})
            else:
                return reverse(
                    "add_an_individual",
                    kwargs={
                        "individual_uuid": str(uuid.uuid4()),
                    },
                )
        else:
            return reverse("your_details")


class YourDetailsView(BaseLicenceFormView):
    form_class = forms.YourDetailsForm

    def get_success_url(self):
        if self.instance.who_do_you_want_the_licence_to_cover == "business":
            return reverse("is_the_business_registered_with_companies_house", kwargs={"business_uuid": str(uuid.uuid4())})
        else:
            return reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": str(uuid.uuid4()),
                },
            )
