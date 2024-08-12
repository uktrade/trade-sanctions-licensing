import logging
import uuid

from apply_for_a_licence.forms import forms_individual as forms
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class AddAnIndividualView(BaseFormView):
    form_class = forms.AddAnIndividualForm
    template_name = "core/base_form_step.html"
    redirect_after_post = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # restore the form data from the individual_uuid, if it exists
        if self.request.method == "GET":
            if individual_uuid := self.request.GET.get("individual_uuid", None):
                if individuals_dict := self.request.session.get("individuals", {}).get(individual_uuid, None):
                    kwargs["data"] = individuals_dict["dirty_data"]

        return kwargs

    def form_valid(self, form: forms.AddAnIndividualForm) -> HttpResponse:
        current_individuals = self.request.session.get("individuals", {})
        # get the individual_uuid if it exists, otherwise create it
        if individual_uuid := self.request.GET.get("individual_uuid", self.kwargs.get("individual_uuid", str(uuid.uuid4()))):
            # used to display the individual_uuid data in individual_added.html
            cleaned_data = form.cleaned_data
            cleaned_data["nationality_and_location"] = dict(form.fields["nationality_and_location"].choices)[
                form.cleaned_data["nationality_and_location"]
            ]
            current_individuals[individual_uuid] = {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        self.request.session["individuals"] = current_individuals
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
        if len(request.session.get("individuals", [])) >= 1:
            return super().dispatch(request, *args, **kwargs)
        return redirect("add_an_individual")

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            return reverse("add_an_individual")
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
