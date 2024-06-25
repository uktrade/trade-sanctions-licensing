from typing import Any

from core.forms.cookie_forms import CookiesConsentForm, HideCookiesForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView


class CookiesConsentView(FormView):
    template_name = "core/cookies_consent.html"
    form_class = CookiesConsentForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        initial_dict = {}

        if current_cookies_policy := self.request.COOKIES.get("accepted_ga_cookies"):
            initial_dict["accept_cookies"] = current_cookies_policy == "true"
            kwargs["initial"] = initial_dict

        # redirect the user back to the page they were on before they were shown the cookie consent form
        if redirect_back_to := self.request.GET.get("redirect_back_to"):
            self.request.session["redirect_back_to"] = redirect_back_to

        return kwargs

    def form_valid(self, form: CookiesConsentForm) -> HttpResponse:
        # cookie consent lasts for 1 year
        cookie_max_age = 365 * 24 * 60 * 60

        if "came_from_cookies_page" in self.request.GET:
            response = redirect(reverse("cookies_consent") + "?cookies_set=true")
        else:
            response = redirect(self.request.session.get("redirect_back_to", "/") + "?cookies_set=true")

        # regardless of their choice, we set a cookie to say they've made a choice
        response.set_cookie("cookie_preferences_set", "true", max_age=cookie_max_age)
        response.set_cookie(
            "accepted_ga_cookies",
            "true" if form.cleaned_data["do_you_want_to_accept_analytics_cookies"] else "false",
            max_age=cookie_max_age,
        )
        return response


class HideCookiesView(FormView):
    template_name = "core/hide_cookies.html"
    form_class = HideCookiesForm

    def form_valid(self, form: HideCookiesForm) -> HttpResponse:
        referrer_url = self.request.session.get("redirect_back_to", "/")
        return redirect(referrer_url)
