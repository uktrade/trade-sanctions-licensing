import logging
from typing import Type

from apply_for_a_licence import choices
from apply_for_a_licence.choices import NationalityAndLocation
from apply_for_a_licence.forms import forms_individual as individual_forms
from apply_for_a_licence.forms import forms_yourself as forms
from apply_for_a_licence.models import Individual
from apply_for_a_licence.views.base_views import DeleteAnEntityView
from apply_for_a_licence.views.views_individual import BaseIndividualFormView
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class AddYourselfView(BaseIndividualFormView):
    form_class = forms.AddYourselfForm
    redirect_after_post = False
    pk_url_kwarg = "yourself_id"
    redirect_with_query_parameters = True

    def get_yourself_id(self):
        if self.request.GET.get("new", ""):
            # The user wants to add a new applicant individual, create it now and assign the id
            # Lookup first to make sure there are no ghost ids
            yourself_individual, created = Individual.objects.get_or_create(
                licence=self.licence_object, status="draft", is_applicant=True
            )
            return yourself_individual.id
        else:
            yourself_id = self.request.GET.get("yourself_id") or self.kwargs[self.pk_url_kwarg]
            if yourself_id:
                return int(yourself_id)

        return None

    def dispatch(self, request, *args, **kwargs):
        if yourself_id := self.get_yourself_id():
            self.kwargs[self.pk_url_kwarg] = yourself_id
        return super().dispatch(request, *args, **kwargs)

    def save_form(self, form):
        # save the form and update the licence object with the applicant's full name
        instance = super().save_form(form)
        licence_object = self.licence_object
        licence_object.applicant_full_name = instance.full_name
        licence_object.save()

        #  This is the applicant individual so marking it as such
        instance.is_applicant = True
        instance.save()

        return instance

    def get_success_url(self):
        is_uk_individual = self.form.cleaned_data["nationality_and_location"] in [
            NationalityAndLocation.uk_national_uk_location.value,
            NationalityAndLocation.dual_national_uk_location.value,
            NationalityAndLocation.non_uk_national_uk_location.value,
        ]

        success_url = reverse(
            "add_yourself_address",
            kwargs={
                "licence_pk": self.kwargs["licence_pk"],
                "yourself_id": self.instance.id,
                "location": "in-uk" if is_uk_individual else "outside-uk",
            },
        )

        return success_url


class AddYourselfAddressView(BaseIndividualFormView):
    pk_url_kwarg = "yourself_id"

    def get_form_class(self) -> Type[forms.AddYourselfUKAddressForm | forms.AddYourselfNonUKAddressForm]:
        yourself_id = self.kwargs.get("yourself_id")
        instance = get_object_or_404(Individual, pk=yourself_id, licence=self.licence_object)

        if instance.nationality_and_location in [
            "uk_national_uk_location",
            "dual_national_uk_location",
            "non_uk_national_uk_location",
        ]:
            form_class = forms.AddYourselfUKAddressForm
        else:
            form_class = forms.AddYourselfNonUKAddressForm
        return form_class

    def save_form(self, form):
        instance = super().save_form(form)
        instance.status = choices.EntityStatusChoices.complete
        instance.save()
        return instance

    def get_success_url(self):
        success_url = reverse("yourself_and_individual_added", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class YourselfAndIndividualAddedView(BaseSaveAndReturnLicenceModelFormView):
    form_class = individual_forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/yourself_and_individual_added.html"

    def dispatch(self, request, *args, **kwargs):
        self.individuals = Individual.objects.filter(licence=self.licence_object)
        if len(self.individuals) > 0:
            # only allow access to this page if an individual or yourself has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse("add_yourself", kwargs={"licence_pk": self.licence_object.id}) + "?new=yes")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["licence_object"] = self.licence_object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        licence_object = self.licence_object
        for individual in self.individuals:
            if individual.full_name == licence_object.applicant_full_name:
                context["yourself"] = individual
                self.individuals = self.individuals.exclude(id=individual.id)
        context["individuals"] = self.individuals

        return context

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            new_individual = Individual.objects.create(licence=self.licence_object)
            return (
                reverse("add_an_individual", kwargs={"licence_pk": self.kwargs["licence_pk"]})
                + f"?individual_id={new_individual.id}"
            )
        else:
            return reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})


class DeleteIndividualFromYourselfView(DeleteAnEntityView):
    model = Individual
    allow_zero_entities = True
    pk_url_kwarg = "individual_id"

    def get_success_url(self):
        success_url = reverse("yourself_and_individual_added", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url
