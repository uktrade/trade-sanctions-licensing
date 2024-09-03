import logging
import urllib.parse
import uuid

from apply_for_a_licence.choices import NationalityAndLocation
from apply_for_a_licence.forms import forms_individual as individual_forms
from apply_for_a_licence.forms import forms_yourself as forms
from apply_for_a_licence.utils import get_form
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class AddYourselfView(BaseFormView):
    form_class = forms.AddYourselfForm

    def form_valid(self, form: forms.AddYourselfForm) -> HttpResponse:
        your_details = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["name_data"] = your_details

        current_individuals = self.request.session.get("individuals", {})
        # get the individual_uuid if it exists, otherwise create it
        if individual_uuid := self.request.GET.get("individual_uuid", str(uuid.uuid4())):
            # used to display the individual_uuid data in individual_added.html
            if individual_uuid not in current_individuals:
                current_individuals[individual_uuid] = {}

            current_individuals[individual_uuid]["name_data"] = your_details
            self.individual_uuid = individual_uuid

            self.request.session["individuals"] = current_individuals

        self.is_uk_individual = form.cleaned_data["nationality_and_location"] in [
            NationalityAndLocation.uk_national_uk_location.value,
            NationalityAndLocation.dual_national_uk_location.value,
            NationalityAndLocation.non_uk_national_uk_location.value,
        ]

        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse(
            "add_yourself_address",
            kwargs={
                "location": "in_the_uk" if self.is_uk_individual else "outside_the_uk",
                "individual_uuid": self.individual_uuid,
            },
        )
        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url


class AddYourselfAddressView(BaseFormView):
    success_url = reverse_lazy("yourself_and_individual_added")

    def get_form_class(self) -> [forms.AddYourselfUKAddressForm | forms.AddYourselfNonUKAddressForm]:
        form_class = forms.AddYourselfNonUKAddressForm

        if add_yourself_view := self.request.session.get("add_yourself", False):
            if add_yourself_view.get("nationality_and_location") in [
                "uk_national_uk_location",
                "dual_national_uk_location",
                "non_uk_national_uk_location",
            ]:
                form_class = forms.AddYourselfUKAddressForm
        return form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # restore the form data from the individual_uuid, if it exists
        if self.request.method == "GET":
            if individual_uuid := self.request.GET.get("individual_uuid", None):
                if individuals_dict := self.request.session.get("individuals", {}).get(individual_uuid, None):
                    kwargs["data"] = individuals_dict["name_data"]["dirty_data"]

        return kwargs

    def form_valid(self, form: forms.AddYourselfUKAddressForm | forms.AddYourselfNonUKAddressForm) -> HttpResponse:
        your_address = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["your_address"] = your_address

        current_individuals = self.request.session.get("individuals", {})
        # get the individual_uuid if it exists, otherwise create it
        if individual_uuid := self.kwargs.get("individual_uuid", str(uuid.uuid4())):
            # used to display the individual_uuid data in individual_added.html
            if individual_uuid not in current_individuals:
                current_individuals[individual_uuid] = {}

            self.request.session["add_yourself_id"] = individual_uuid
            self.request.session["add_yourself_address"] = your_address
            current_individuals[individual_uuid]["address_data"] = your_address
            self.individual_uuid = individual_uuid

            # is it a UK address?
            self.is_uk_individual = form.cleaned_data["url_location"] == "in_the_uk"
            self.request.session["individuals"] = current_individuals

        return super().form_valid(form)


class YourselfAndIndividualAddedView(BaseFormView):
    form_class = individual_forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/yourself_and_individual_added.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["yourself_form"] = get_form(self.request, "add_yourself")
        return context

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            return reverse("add_an_individual") + "?change=yes"
        else:
            return reverse("previous_licence")


class DeleteIndividualFromYourselfView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        redirect_to = redirect(reverse_lazy("yourself_and_individual_added"))
        if individual_uuid := self.request.POST.get("individual_uuid"):
            individuals = self.request.session.get("individuals", None)
            individuals.pop(individual_uuid, None)
            self.request.session["individuals"] = individuals
        return redirect_to
