import logging
from typing import Any, Dict, Type

from apply_for_a_licence import choices
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
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class BaseIndividualFormView(AddAnEntityView):
    pk_url_kwarg = "individual_id"
    model = Individual
    context_object_name = "individuals"


class AddAnIndividualView(BaseIndividualFormView):
    form_class = forms.AddAnIndividualForm
    redirect_after_post = False
    redirect_with_query_parameters = True

    def get_individual_id(self):
        if self.request.GET.get("redirect_to_url", "") == "check_your_answers" or self.request.GET.get("change", ""):
            # The user wants to add a new individual
            new_individual, created = Individual.objects.get_or_create(licence=self.licence_object, status="draft")
            return new_individual.id
        else:
            individual_id = self.request.GET.get("individual_id") or self.kwargs[self.pk_url_kwarg]
            if individual_id:
                try:
                    return int(individual_id)
                except Exception as err:
                    raise err
        return None

    def dispatch(self, request, *args, **kwargs):
        if individual_id := self.get_individual_id():
            self.kwargs[self.pk_url_kwarg] = individual_id
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        is_uk_individual = self.form.cleaned_data["nationality_and_location"] in [
            NationalityAndLocation.uk_national_uk_location.value,
            NationalityAndLocation.dual_national_uk_location.value,
            NationalityAndLocation.non_uk_national_uk_location.value,
        ]
        success_url = reverse(
            "what_is_individuals_address",
            kwargs={
                "location": "in-uk" if is_uk_individual else "outside-uk",
                "individual_id": self.kwargs.get("individual_id"),
            },
        )
        return success_url


class DeleteIndividualView(DeleteAnEntityView):
    model = Individual
    success_url = reverse_lazy("individual_added")
    pk_url_kwarg = "individual_id"


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

    def save_form(self, form):
        instance = form.save(commit=False)
        # the individual should now be marked as 'complete'
        instance.status = choices.EntityStatusChoices.complete
        instance.save()
        return instance


class IndividualAddedView(BaseSaveAndReturnFormView):
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/individual_added.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["licence_object"] = self.licence_object
        return kwargs

    def get_all_individuals(self) -> QuerySet[Individual]:
        return Individual.objects.filter(licence=self.licence_object)

    def dispatch(self, request, *args, **kwargs):
        individuals = self.get_all_individuals()
        if len(individuals) > 0:
            # only allow access to this page if an individual has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(self.get_success_url())

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["individuals"] = self.get_all_individuals()
        return context

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            new_individual = Individual.objects.create(
                licence=self.licence_object,
            )
            success_url = reverse("add_an_individual") + f"?individual_id={new_individual.id}&change=yes"
        elif self.licence_object.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.individual:
            success_url = reverse("business_employing_individual")
        else:
            success_url = reverse("tasklist")

        return success_url


class BusinessEmployingIndividualView(BaseSaveAndReturnModelFormView):
    form_class = forms.BusinessEmployingIndividualForm
    success_url = reverse_lazy("tasklist")

    @property
    def object(self) -> Organisation:
        instance, _ = Organisation.objects.get_or_create(
            licence=self.licence_object,
            type_of_relationship=TypeOfRelationshipChoices.named_individuals,
            defaults={"status": choices.EntityStatusChoices.draft},
        )
        return instance

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if Individual.objects.filter(licence=self.licence_object).count() > 1:
            kwargs["form_h1_header"] = "Details of the business employing the individuals"
        else:
            kwargs["form_h1_header"] = "Details of the business employing the individual"

        kwargs["instance"] = self.object
        return kwargs

    def save_form(self, form):
        instance = form.save(commit=False)
        instance.status = choices.EntityStatusChoices.complete
        instance.save()
        return instance
