import logging
import urllib.parse
import uuid
from typing import Any

from apply_for_a_licence.choices import NationalityAndLocation
from apply_for_a_licence.forms import forms_individual as forms
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class AddAnIndividualView(AddAnEntityView):
    form_class = forms.AddAnIndividualForm
    redirect_after_post = False
    session_key = "individuals"
    url_parameter_key = "individual_uuid"

    def set_session_data(self, form: forms.AddAnIndividualForm) -> dict[str, Any]:
        return {
            "name_data": {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        }

    def get_session_data(self, session_data: dict[str, Any]) -> dict[str, Any]:
        return session_data["name_data"]["dirty_data"]

    def form_valid(self, form: forms.AddAnIndividualForm) -> HttpResponse:
        # is it a UK address?
        self.is_uk_individual = form.cleaned_data["nationality_and_location"] in [
            NationalityAndLocation.uk_national_uk_location.value,
            NationalityAndLocation.dual_national_uk_location.value,
            NationalityAndLocation.non_uk_national_uk_location.value,
        ]
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse(
            "what_is_individuals_address",
            kwargs={
                "location": "in-uk" if self.is_uk_individual else "outside-uk",
                "individual_uuid": self.entity_uuid,
            },
        )
        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url


class DeleteIndividualView(DeleteAnEntityView):
    success_url = reverse_lazy("individual_added")
    session_key = "individuals"
    url_parameter_key = "individual_uuid"


class WhatIsIndividualsAddressView(AddAnEntityView):
    url_parameter_key = "individual_uuid"
    session_key = "individuals"

    def set_session_data(self, form: forms.AddAnIndividualForm) -> dict[str, Any]:
        return {
            "address_data": {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        }

    def get_session_data(self, session_data: dict[str, Any]) -> dict[str, Any]:
        return session_data.get("address_data", {}).get("dirty_data", {})

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_class(self) -> forms.IndividualUKAddressForm | forms.IndividualNonUKAddressForm:
        if self.location == "in-uk":
            form_class = forms.IndividualUKAddressForm
        else:
            form_class = forms.IndividualNonUKAddressForm
        return form_class

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.method == "GET" and not form.data:
            form.is_bound = False
        return form

    def get_success_url(self):
        success_url = reverse("individual_added")
        if start_view := self.request.session.get("start", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
                success_url = reverse("yourself_and_individual_added")
        return success_url


class IndividualAddedView(BaseFormView):
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/individual_added.html"

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            return reverse("add_an_individual", kwargs={"individual_uuid": uuid.uuid4()}) + "?change=yes"
        else:
            return reverse("previous_licence")


class BusinessEmployingIndividualView(BaseFormView):
    form_class = forms.BusinessEmployingIndividualForm
    success_url = reverse_lazy("type_of_service")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if len(self.request.session.get("individuals", {})) == 1:
            kwargs["form_h1_header"] = "Details of the business employing the individual"
        else:
            kwargs["form_h1_header"] = "Details of the business employing the individuals"

        return kwargs
