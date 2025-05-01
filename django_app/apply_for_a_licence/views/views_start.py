import logging

from apply_for_a_licence.forms import forms_start as forms
from apply_for_a_licence.models import Licence
from core.decorators import reset_last_activity_session_timestamp
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
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
        return instance

    def get_success_url(self):
        success_url = reverse("start", kwargs={"licence_pk": self.instance.pk})
        return success_url


@method_decorator(reset_last_activity_session_timestamp, name="dispatch")
class StartView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.StartForm

    def form_valid(self, form: forms.StartForm) -> HttpResponse:
        if previous_answer := self.licence_object.who_do_you_want_the_licence_to_cover:
            if previous_answer != form.cleaned_data["who_do_you_want_the_licence_to_cover"]:
                # The applicant has changed their answer, remove their previously entered licence data
                Licence.objects.filter(pk=self.licence_object.id).delete()
                self.request.session.pop("licence_id", None)

                new_licence = Licence.objects.create(
                    user=self.request.user,
                    who_do_you_want_the_licence_to_cover=form.cleaned_data["who_do_you_want_the_licence_to_cover"],
                )

                self.request.session["licence_id"] = new_licence.id
                self.request.session.save()
                self._licence_object = new_licence

                return redirect(reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]}))

        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class ThirdPartyView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.ThirdPartyForm

    def get_success_url(self):
        success_url = reverse("your_details", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class YourDetailsView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.YourDetailsForm

    def get_success_url(self):
        success_url = reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url
