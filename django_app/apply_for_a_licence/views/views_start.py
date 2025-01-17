import logging
import uuid
from typing import Any

from apply_for_a_licence.forms import forms_start as forms
from apply_for_a_licence.fsm import StartJourneyMachine
from apply_for_a_licence.models import Licence
from core.forms.base_forms import GenericForm
from core.utils import update_last_activity_session_timestamp
from core.views.base_views import BaseFormView
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from utils.notifier import verify_email

logger = logging.getLogger(__name__)


class StartView(BaseFormView):
    form_class = forms.StartForm
    start_journey: StartJourneyMachine

    def dispatch(self, request, *args, **kwargs):
        # refresh the session expiry timestamp. This is the start of the session
        update_last_activity_session_timestamp(request)
        licence_object = Licence.objects.first()
        # create the start journey finite state machine and save to the session
        self.start_journey = StartJourneyMachine(licence_object)
        print(self.start_journey.state)
        print(self.start_journey.states)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str | None:
        # increment the state machine
        self.start_journey.start_chosen()
        print(self.start_journey.state)
        return reverse(self.start_journey.state)


class ThirdPartyView(BaseFormView):
    form_class = forms.ThirdPartyForm
    success_url = reverse_lazy("what_is_your_email")


class WhatIsYouEmailAddressView(BaseFormView):
    form_class = forms.WhatIsYourEmailForm
    success_url = reverse_lazy("email_verify")

    def form_valid(self, form: forms.WhatIsYourEmailForm) -> HttpResponse:
        user_email = form.cleaned_data["email"]
        self.request.session["user_email_address"] = user_email
        verify_email(user_email, self.request)
        return super().form_valid(form)


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class EmailVerifyView(BaseFormView):
    form_class = forms.EmailVerifyForm

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if form_h1_header := getattr(forms.WhatIsYourEmailForm, "form_h1_header"):
            context["form_h1_header"] = form_h1_header
        return context

    def get_success_url(self) -> str:
        start_view = self.request.session.get("start", False)
        if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
            return reverse("add_yourself")
        else:
            return reverse("your_details")


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class RequestVerifyCodeView(BaseFormView):
    form_class = GenericForm
    template_name = "apply_for_a_licence/form_steps/request_verify_code.html"
    success_url = reverse_lazy("email_verify")

    def form_valid(self, form: GenericForm) -> HttpResponse:
        user_email_address = self.request.session["user_email_address"]
        if getattr(self.request, "limited", False):
            logger.warning(f"User has been rate-limited: {user_email_address}")
            return self.form_invalid(form)
        verify_email(user_email_address, self.request)
        return super().form_valid(form)


class YourDetailsView(BaseFormView):
    form_class = forms.YourDetailsForm

    def get_success_url(self):
        if start_view := self.request.session.get("start", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "business":
                return reverse("is_the_business_registered_with_companies_house")
            else:
                return reverse(
                    "add_an_individual",
                    kwargs={
                        "individual_uuid": str(uuid.uuid4()),
                    },
                )
