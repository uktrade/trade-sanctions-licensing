import logging
import urllib.parse
import uuid
from typing import Any, Dict

from apply_for_a_licence.choices import (
    NationalityAndLocation,
    TypeOfRelationshipChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
)
from apply_for_a_licence.forms import forms_individual as forms
from apply_for_a_licence.models import Individual, Licence, Organisation
from apply_for_a_licence.views.base_views import DeleteAnEntitySaveAndReturnView
from core.views.base_views import BaseFormView, BaseIndividualFormView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class AddAnIndividualView(BaseFormView):
    form_class = forms.AddAnIndividualForm
    redirect_after_post = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        individual_id = self.kwargs.get("individual_uuid")
        licence_id = self.request.session["licence_id"]
        licence_object = get_object_or_404(Licence, pk=licence_id)
        # get_or_create returns tuple
        instance, _ = Individual.objects.get_or_create(pk=individual_id, licence=licence_object)
        kwargs["instance"] = instance
        return kwargs

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
                "individual_uuid": self.kwargs.get("individual_uuid"),
            },
        )
        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url


class DeleteIndividualView(DeleteAnEntitySaveAndReturnView):
    model = Individual
    success_url = reverse_lazy("individual_added")


class WhatIsIndividualsAddressView(BaseIndividualFormView):

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
        licence_id = self.request.session["licence_id"]
        licence_object = Licence.objects.get(pk=licence_id)
        if licence_object.who_do_you_want_the_licence_to_cover == WhoDoYouWantTheLicenceToCoverChoices.myself:
            success_url = reverse("yourself_and_individual_added")
        return success_url


class IndividualAddedView(BaseFormView):
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/individual_added.html"

    def dispatch(self, request, *args, **kwargs):
        licence_id = self.request.session["licence_id"]
        licence_object = Licence.objects.get(pk=licence_id)
        individuals = Individual.objects.filter(licence=licence_object)
        if len(individuals) > 0:
            # only allow access to this page if an individual has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("add_an_individual", kwargs={"individual_uuid": uuid.uuid4()})

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        licence_id = self.request.session["licence_id"]
        licence_object = Licence.objects.get(pk=licence_id)
        context["individuals"] = Individual.objects.filter(licence=licence_object)
        return context

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
        licence_id = self.request.session["licence_id"]
        licence_object = get_object_or_404(Licence, pk=licence_id)
        individuals = Individual.objects.filter(licence=licence_object)
        instance, _ = Organisation.objects.get_or_create(
            licence=licence_object, type_of_relationship=TypeOfRelationshipChoices.named_individuals
        )
        if len(individuals) == 1:
            kwargs["form_h1_header"] = "Details of the business employing the individual"
        else:
            kwargs["form_h1_header"] = "Details of the business employing the individuals"

        kwargs["instance"] = instance
        return kwargs
