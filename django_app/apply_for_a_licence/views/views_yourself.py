import logging
from typing import Any

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
    success_url = reverse_lazy("add_yourself_address")


class AddYourselfAddressView(BaseFormView):
    form_class = forms.AddYourselfAddressForm
    success_url = reverse_lazy("yourself_and_individual_added")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()

        if add_yourself_view := self.request.session.get("add_yourself", False):
            if add_yourself_view.get("nationality_and_location") in [
                "uk_national_uk_location",
                "dual_national_uk_location",
                "non_uk_national_uk_location",
            ]:
                kwargs["is_uk_address"] = True
        return kwargs

    def form_valid(self, form: forms.AddYourselfAddressForm) -> HttpResponse:
        your_address = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["your_address"] = your_address
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
