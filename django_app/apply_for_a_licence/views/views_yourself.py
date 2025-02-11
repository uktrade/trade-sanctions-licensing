import logging
import uuid
from typing import Type

from apply_for_a_licence.choices import NationalityAndLocation
from apply_for_a_licence.forms import forms_individual as individual_forms
from apply_for_a_licence.forms import forms_yourself as forms
from apply_for_a_licence.models import Individual
from apply_for_a_licence.views.base_views import DeleteAnEntityView
from apply_for_a_licence.views.views_individual import BaseIndividualFormView
from core.utils import get_licence_object
from core.views.base_views import BaseSaveAndReturnFormView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class AddYourselfView(BaseIndividualFormView):
    form_class = forms.AddYourselfForm
    redirect_after_post = False
    pk_url_kwarg = "yourself_uuid"

    def dispatch(self, request, *args, **kwargs):
        Individual.objects.get_or_create(pk=self.kwargs["yourself_uuid"], licence=self.licence_object)
        return super().dispatch(request, *args, **kwargs)

    def save_form(self, form):
        # save the form and update the licence object with the applicant's full name
        instance = super().save_form(form)
        licence_object = self.licence_object
        licence_object.applicant_full_name = instance.full_name
        licence_object.save()
        return instance

    def get_success_url(self):
        licence_object = self.licence_object
        licence_object.applicant_full_name = self.instance.full_name
        licence_object.save()

        is_uk_individual = self.form.cleaned_data["nationality_and_location"] in [
            NationalityAndLocation.uk_national_uk_location.value,
            NationalityAndLocation.dual_national_uk_location.value,
            NationalityAndLocation.non_uk_national_uk_location.value,
        ]

        success_url = reverse(
            "add_yourself_address",
            kwargs={
                "yourself_uuid": self.instance.id,
                "location": "in-uk" if is_uk_individual else "outside-uk",
            },
        )

        # changed from UK address to another address or vice versa
        if self.form.has_field_changed("nationality_and_location"):
            self.request.session["add_yourself_address"] = {}

        return success_url


class AddYourselfAddressView(BaseIndividualFormView):
    success_url = reverse_lazy("yourself_and_individual_added")
    pk_url_kwarg = "yourself_uuid"

    def get_form_class(self) -> Type[forms.AddYourselfUKAddressForm | forms.AddYourselfNonUKAddressForm]:
        yourself_id = self.kwargs.get("yourself_uuid")
        licence_object = get_licence_object(self.request)
        instance = get_object_or_404(Individual, pk=yourself_id, licence=licence_object)

        if instance.nationality_and_location in [
            "uk_national_uk_location",
            "dual_national_uk_location",
            "non_uk_national_uk_location",
        ]:
            form_class = forms.AddYourselfUKAddressForm
        else:
            form_class = forms.AddYourselfNonUKAddressForm
        return form_class


class YourselfAndIndividualAddedView(BaseSaveAndReturnFormView):
    form_class = individual_forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/yourself_and_individual_added.html"

    def dispatch(self, request, *args, **kwargs):
        licence_object = get_licence_object(self.request)
        self.individuals = Individual.objects.filter(licence=licence_object)
        if len(self.individuals) > 0:
            # only allow access to this page if an individual or yourself has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("add_yourself")

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
            return (
                reverse(
                    "add_an_individual",
                    kwargs={
                        "individual_uuid": uuid.uuid4(),
                    },
                )
                + "?change=yes"
            )
        else:
            return reverse("previous_licence")


class DeleteIndividualFromYourselfView(DeleteAnEntityView):
    model = Individual
    success_url = reverse_lazy("yourself_and_individual_added")
    allow_zero_entities = True
    pk_url_kwarg = "pk"
