import logging
from typing import Any

from core.views.base_views import BaseFormView
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit
from utils.notifier import verify_email

from . import forms

logger = logging.getLogger(__name__)


class StartView(BaseFormView):
    form_class = forms.StartForm

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["who_do_you_want_the_licence_to_cover"]

        if answer in ["business", "individual"]:
            return reverse("are_you_third_party")
        elif answer == "myself":
            return reverse("what_is_your_email")


class ThirdPartyView(BaseFormView):
    form_class = forms.ThirdPartyForm


class WhatIsYouEmailAddressView(BaseFormView):
    form_class = forms.WhatIsYourEmailForm
    success_url = reverse_lazy("email_verify")

    def form_valid(self, form: forms.WhatIsYourEmailForm) -> HttpResponse:
        user_email = form.cleaned_data["email"]
        self.request.session["user_email_address"] = user_email
        self.request.session.modified = True
        verify_email(user_email, self.request)
        return super().form_valid(form)


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class EmailVerifyView(BaseFormView):
    form_class = forms.EmailVerifyForm
    success_url = reverse_lazy("complete")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super(EmailVerifyView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if form_h1_header := getattr(forms.WhatIsYourEmailForm, "form_h1_header"):
            context["form_h1_header"] = form_h1_header
        return context


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class RequestVerifyCodeView(BaseFormView):
    form_class = forms.SummaryForm
    template_name = "apply_for_a_licence/form_steps/request_verify_code.html"
    success_url = reverse_lazy("email_verify")

    def form_valid(self, form: forms.SummaryForm) -> HttpResponse:
        user_email_address = self.request.session["user_email_address"]
        if getattr(self.request, "limited", False):
            logger.warning(f"User has been rate-limited: {user_email_address}")
            return self.form_invalid(form)
        verify_email(user_email_address, self.request)
        return super().form_valid(form)


class CompleteView(TemplateView):
    template_name = "apply_for_a_licence/complete.html"


class YourDetailsView(BaseFormView):
    form_class = forms.YourDetailsForm

    def get_success_url(self):
        return reverse("previous_licence")


class AddABusinessView(BaseFormView):
    form_class = forms.AddABusinessForm

    def get_success_url(self):
        return reverse("business_added")


class AddAnIndividualView(BaseFormView):
    form_class = forms.AddAnIndividualForm

    def get_success_url(self):
        return reverse("individual_added")


class IndividualAddedView(BaseFormView):
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/individual_added.html"

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            return reverse("add_an_individual")
        else:
            return reverse("previous_licence")


class DeleteIndividualView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        redirect_to = redirect(reverse_lazy("apply_for_a_licence:individual_added_view"))
        if individual_uuid := self.request.POST.get("individual_uuid"):
            individuals = self.request.session.pop("indvidual_uuid", None)
            individuals.pop(individual_uuid, None)
            self.request.session["individuals"] = individuals
            self.request.session.modified = True
            if len(individuals) == 0:
                redirect_to = redirect(reverse_lazy("apply_for_a_licence:zero_individuals"))
        return redirect_to


class ZeroIndividualsView(BaseFormView):
    form_class = forms.ZeroIndividualsForm

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        add_individual = self.form.cleaned_data["do_you_want_to_add_an_individual"]
        if add_individual:
            return reverse_lazy("apply_for_a_licence:add_an_individual")
        else:
            return reverse_lazy("apply_for_a_licence:previous_licence")
