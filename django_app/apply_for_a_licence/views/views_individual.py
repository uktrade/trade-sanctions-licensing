import logging
import urllib.parse
import uuid

from apply_for_a_licence.choices import NationalityAndLocation
from apply_for_a_licence.forms import forms_individual as forms
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class AddAnIndividualView(BaseFormView):
    form_class = forms.AddAnIndividualForm

    @property
    def redirect_after_post(self) -> bool:
        if self.request.GET.get("new", None) == "yes":
            # if we want to create a new individual, we need want to redirect the user to the next page so they can
            # provide the rest of the information
            return False
        else:
            return True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.method == "GET" and self.request.GET.get("new", None) == "yes":
            form.is_bound = False
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # restore the form data from the individual_uuid, if it exists
        if self.request.method == "GET":
            if individual_uuid := self.kwargs.get("individual_uuid", None):
                if individuals_dict := self.request.session.get("individuals", {}).get(individual_uuid, None):
                    kwargs["data"] = individuals_dict["name_data"]["dirty_data"]

        return kwargs

    def form_valid(self, form: forms.AddAnIndividualForm) -> HttpResponse:
        current_individuals = self.request.session.get("individuals", {})
        # get the individual_uuid if it exists, otherwise create it
        individual_uuid = self.kwargs["individual_uuid"]
        # used to display the individual_uuid data in individual_added.html
        if individual_uuid not in current_individuals:
            current_individuals[individual_uuid] = {}

        current_individuals[individual_uuid]["name_data"] = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.individual_uuid = individual_uuid

        # is it a UK address?
        self.is_uk_individual = form.cleaned_data["nationality_and_location"] in [
            NationalityAndLocation.uk_national_uk_location.value,
            NationalityAndLocation.dual_national_uk_location.value,
            NationalityAndLocation.non_uk_national_uk_location.value,
        ]
        self.request.session["individuals"] = current_individuals
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse(
            "what_is_individuals_address",
            kwargs={
                "location": "in_the_uk" if self.is_uk_individual else "outside_the_uk",
                "individual_uuid": self.individual_uuid,
            },
        )
        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url


class WhatIsIndividualsAddressView(BaseFormView):

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        self.has_address_data = False
        if self.request.method == "GET":
            # restore the form data for that individual UUID in the session
            current_individual = self.request.session.get("individuals", {}).get(self.kwargs["individual_uuid"], {})
            if address_data := current_individual.get("address_data", None):
                kwargs["data"] = address_data["dirty_data"]
                self.has_address_data = True
        return kwargs

    def get_form_class(self) -> [forms.IndividualUKAddressForm | forms.IndividualNonUKAddressForm]:
        if self.location == "in_the_uk":
            form_class = forms.IndividualUKAddressForm
        else:
            form_class = forms.IndividualNonUKAddressForm
        return form_class

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.method == "GET" and not self.has_address_data:
            form.is_bound = False
        return form

    def form_valid(self, form):
        individuals = self.request.session.get("individuals", {})
        individuals[self.kwargs["individual_uuid"]]["address_data"] = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["individuals"] = individuals
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse("individual_added")
        if start_view := self.request.session.get("start", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
                success_url = reverse("yourself_and_individual_added")
        return success_url


class IndividualAddedView(BaseFormView):
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/individual_added.html"

    def dispatch(self, request, *args, **kwargs):
        if request.session.get("individuals", None):
            return super().dispatch(request, *args, **kwargs)
        return redirect("add_an_individual")

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            new_individual = str(uuid.uuid4())
            return reverse("add_an_individual", kwargs={"individual_uuid": new_individual}) + "?new=yes"
        else:
            return reverse("previous_licence")


class DeleteIndividualView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        individuals = self.request.session.get("individuals", [])
        # at least one individual must be added
        if len(individuals) > 1:
            if individual_uuid := self.request.POST.get("individual_uuid"):
                individuals.pop(individual_uuid, None)
                self.request.session["individuals"] = individuals
        return redirect(reverse_lazy("individual_added"))


class BusinessEmployingIndividualView(BaseFormView):
    form_class = forms.BusinessEmployingIndividualForm
    success_url = reverse_lazy("type_of_service")
