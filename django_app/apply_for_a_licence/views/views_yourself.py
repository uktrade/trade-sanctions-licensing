import logging
import urllib.parse
import uuid

from apply_for_a_licence.choices import NationalityAndLocation
from apply_for_a_licence.forms import forms_individual as individual_forms
from apply_for_a_licence.forms import forms_yourself as forms
from apply_for_a_licence.models import Individual, Licence
from apply_for_a_licence.views.base_views import DeleteAnEntitySaveAndReturnView
from core.views.base_views import BaseFormView, BaseIndividualFormView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class AddYourselfView(BaseFormView):
    form_class = forms.AddYourselfForm
    redirect_after_post = False

    def __init__(self):
        self.instance = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        yourself_id = self.kwargs.get("yourself_uuid")
        licence_id = self.request.session["licence_id"]
        licence_object = get_object_or_404(Licence, pk=licence_id)
        # get_or_create returns tuple
        instance, _ = Individual.objects.get_or_create(pk=yourself_id, licence=licence_object)
        kwargs["instance"] = instance
        self.instance = instance
        return kwargs

    def form_valid(self, form: forms.AddYourselfForm) -> HttpResponse:
        self.is_uk_individual = form.cleaned_data["nationality_and_location"] in [
            NationalityAndLocation.uk_national_uk_location.value,
            NationalityAndLocation.dual_national_uk_location.value,
            NationalityAndLocation.non_uk_national_uk_location.value,
        ]

        return super().form_valid(form)

    def get_success_url(self):
        licence_id = self.request.session["licence_id"]
        licence_object = get_object_or_404(Licence, pk=licence_id)
        licence_object.applicant_full_name = self.instance.full_name
        licence_object.save()

        success_url = reverse(
            "add_yourself_address",
            kwargs={
                "yourself_uuid": self.instance.id,
                "location": "in-uk" if self.is_uk_individual else "outside-uk",
            },
        )

        # changed from UK address to another address or vice versa
        if "nationality_and_location" in self.changed_fields:
            self.request.session["add_yourself_address"] = {}

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url


class AddYourselfAddressView(BaseIndividualFormView):
    success_url = reverse_lazy("yourself_and_individual_added")
    pk_url_kwarg = "yourself_uuid"

    def get_form_class(self) -> forms.AddYourselfUKAddressForm | forms.AddYourselfNonUKAddressForm:
        form_class = forms.AddYourselfNonUKAddressForm
        yourself_id = self.kwargs.get("yourself_uuid")
        licence_id = self.request.session["licence_id"]
        licence_object = get_object_or_404(Licence, pk=licence_id)
        instance = get_object_or_404(Individual, pk=yourself_id, licence=licence_object)

        if instance.nationality_and_location in [
            "uk_national_uk_location",
            "dual_national_uk_location",
            "non_uk_national_uk_location",
        ]:
            form_class = forms.AddYourselfUKAddressForm
        return form_class

    def form_valid(self, form: forms.AddYourselfUKAddressForm | forms.AddYourselfNonUKAddressForm) -> HttpResponse:
        # is it a UK address?
        self.is_uk_individual = form.cleaned_data["url_location"] == "in-uk"

        return super().form_valid(form)


class YourselfAndIndividualAddedView(BaseFormView):
    form_class = individual_forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/yourself_and_individual_added.html"

    def dispatch(self, request, *args, **kwargs):
        licence_id = self.request.session["licence_id"]
        licence_object = Licence.objects.get(pk=licence_id)
        individuals = Individual.objects.filter(licence=licence_object)
        if len(individuals) > 0:
            # only allow access to this page if an individual or yourself has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("add_yourself")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        licence_id = self.request.session["licence_id"]
        licence_object = Licence.objects.get(pk=licence_id)
        individuals = Individual.objects.filter(licence=licence_object)
        for individual in individuals:
            if individual.full_name == licence_object.applicant_full_name:
                context["yourself"] = individual
                individuals = individuals.exclude(id=individual.id)
        context["individuals"] = individuals

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


class DeleteIndividualFromYourselfView(DeleteAnEntitySaveAndReturnView):
    model = Individual
    success_url = reverse_lazy("yourself_and_individual_added")
    allow_zero_entities = True
