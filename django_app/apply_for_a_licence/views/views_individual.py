import logging
import uuid
from typing import Any, Dict, Type

from apply_for_a_licence.choices import (
    NationalityAndLocation,
    TypeOfRelationshipChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
)
from apply_for_a_licence.forms import forms_individual as forms
from apply_for_a_licence.models import Individual, Organisation
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.views.base_views import (
    BaseSaveAndReturnFormView,
    BaseSaveAndReturnModelFormView,
)
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class BaseIndividualFormView(AddAnEntityView):
    pk_url_kwarg = "individual_uuid"
    model = Individual
    context_object_name = "individuals"


class AddAnIndividualView(BaseIndividualFormView):
    form_class = forms.AddAnIndividualForm
    redirect_after_post = False

    def dispatch(self, request, *args, **kwargs):
        Individual.objects.get_or_create(pk=self.kwargs["individual_uuid"], defaults={"licence": self.licence_object})
        return super().dispatch(request, *args, **kwargs)

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
        return success_url


class DeleteIndividualView(DeleteAnEntityView):
    model = Individual
    success_url = reverse_lazy("individual_added")
    pk_url_kwarg = "pk"


class WhatIsIndividualsAddressView(BaseIndividualFormView):

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_class(self) -> Type[forms.IndividualUKAddressForm | forms.IndividualNonUKAddressForm]:
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
        if self.licence_object.who_do_you_want_the_licence_to_cover == WhoDoYouWantTheLicenceToCoverChoices.myself:
            success_url = reverse("yourself_and_individual_added")
        return success_url


class IndividualAddedView(BaseSaveAndReturnFormView):
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/individual_added.html"

    def get_all_individuals(self) -> QuerySet[Individual]:
        return Individual.objects.filter(licence=self.licence_object)

    def dispatch(self, request, *args, **kwargs):
        individuals = self.get_all_individuals()
        if len(individuals) > 0:
            # only allow access to this page if an individual has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("add_an_individual", kwargs={"individual_uuid": uuid.uuid4()})

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["individuals"] = self.get_all_individuals()
        return context

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            return reverse("add_an_individual", kwargs={"individual_uuid": uuid.uuid4()}) + "?change=yes"
        else:
            return reverse("previous_licence")


class BusinessEmployingIndividualView(BaseSaveAndReturnModelFormView):
    form_class = forms.BusinessEmployingIndividualForm
    success_url = reverse_lazy("type_of_service")

    @property
    def object(self) -> Organisation:
        instance, _ = Organisation.objects.get_or_create(
            licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.named_individuals
        )
        return instance

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if Individual.objects.filter(licence=self.licence_object).count() == 1:
            kwargs["form_h1_header"] = "Details of the business employing the individual"
        else:
            kwargs["form_h1_header"] = "Details of the business employing the individuals"

        kwargs["instance"] = self.object
        return kwargs
