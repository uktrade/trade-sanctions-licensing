import logging
import urllib.parse
import uuid
from typing import Any, Dict

from apply_for_a_licence.forms import forms_business as forms
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.views.base_views import BaseFormView
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)


class AddABusinessView(AddAnEntityView):
    success_url = reverse_lazy("business_added")
    redirect_after_post = False
    session_key = "businesses"
    url_parameter_key = "business_uuid"

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_class(self):
        if self.location == "in-uk":
            form_class = forms.AddAUKBusinessForm
        else:
            form_class = forms.AddANonUKBusinessForm
        return form_class


class BusinessAddedView(BaseFormView):
    form_class = forms.BusinessAddedForm
    template_name = "apply_for_a_licence/form_steps/business_added.html"

    def dispatch(self, request, *args, **kwargs):
        if request.session.get("businesses", []):
            # only allow access to this page if a business has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("is_the_business_registered_with_companies_house")

    def get_success_url(self):
        add_business = self.form.cleaned_data["do_you_want_to_add_another_business"]
        if add_business:
            return reverse("is_the_business_registered_with_companies_house") + "?change=yes"
        else:
            return reverse("previous_licence")


class DeleteBusinessView(DeleteAnEntityView):
    session_key = "businesses"
    url_parameter_key = "business_uuid"
    success_url = reverse_lazy("business_added")


class IsTheBusinessRegisteredWithCompaniesHouseView(BaseFormView):
    form_class = forms.IsTheBusinessRegisteredWithCompaniesHouseForm
    redirect_after_post = False

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["business_registered_on_companies_house"]

        if answer == "yes":
            success_url = reverse("do_you_know_the_registered_company_number")
        else:
            success_url = reverse("where_is_the_business_located", kwargs={"business_uuid": uuid.uuid4()})

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class DoYouKnowTheRegisteredCompanyNumberView(BaseFormView):
    form_class = forms.DoYouKnowTheRegisteredCompanyNumberForm
    template_name = "apply_for_a_licence/form_steps/conditional_radios_form.html"
    redirect_after_post = False

    def form_valid(self, form: forms.DoYouKnowTheRegisteredCompanyNumberForm) -> HttpResponse:
        # we want to add companies house businesses to the companies house business list
        companies_house_businesses = self.request.session.get("companies_house_businesses", {})
        # get the business_uuid if it exists, otherwise create it
        self.business_uuid = self.request.GET.get("business_uuid", str(uuid.uuid4()))
        # used to display the business_uuid data in business_added.html

        companies_house_businesses[self.business_uuid] = {
            "cleaned_data": {
                "company_number": form.cleaned_data["registered_company_number"],
                "name": form.cleaned_data["registered_company_name"],
                "readable_address": form.cleaned_data["registered_office_address"],
                "companies_house": True,
            },
            "dirty_data": form.data,
        }
        self.request.session["companies_house_businesses"] = companies_house_businesses
        return super().form_valid(form)

    def get_success_url(self) -> str:
        do_you_know_the_registered_company_number = self.form.cleaned_data["do_you_know_the_registered_company_number"]
        registered_company_number = self.form.cleaned_data["registered_company_number"]
        if do_you_know_the_registered_company_number == "yes" and registered_company_number:
            if self.request.session.pop("company_details_500", None):
                success_url = reverse("manual_companies_house_input")
            else:
                success_url = reverse("check_company_details", kwargs={"business_uuid": self.business_uuid})
        else:
            current_businesses = self.request.session.get("businesses", {})
            current_businesses.pop(self.business_uuid, None)
            success_url = reverse("where_is_the_business_located", kwargs={"business_uuid": uuid.uuid4()})

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data()
        context["page_title"] = "Registered Company Number"
        return context


class ManualCompaniesHouseInputView(BaseFormView):
    form_class = forms.ManualCompaniesHouseInputForm
    template_name = "apply_for_a_licence/form_steps/manual_companies_house_input.html"

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["manual_companies_house_input"]
        return reverse("add_a_business", kwargs={"location": location, "business_uuid": uuid.uuid4()})


class CheckCompanyDetailsView(BaseFormView):
    template_name = "apply_for_a_licence/form_steps/check_company_details.html"
    form_class = forms.BaseForm
    success_url = reverse_lazy("business_added")

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["company_details"] = self.request.session["companies_house_businesses"][self.kwargs["business_uuid"]][
            "cleaned_data"
        ]
        context["business_uuid"] = self.kwargs["business_uuid"]
        return context

    def form_valid(self, form):
        # we want to add companies house businesses to the business list
        current_businesses = self.request.session.get("businesses", {})
        # get the business_uuid if it exists, otherwise create it
        self.business_uuid = self.request.GET.get("business_uuid", str(uuid.uuid4()))
        # used to display the business_uuid data in business_added.html
        company_details = self.request.session["companies_house_businesses"][self.kwargs["business_uuid"]]["cleaned_data"]
        company_details_dirty_data = self.request.session["companies_house_businesses"][self.kwargs["business_uuid"]][
            "dirty_data"
        ]
        print(company_details)
        current_businesses[self.business_uuid] = {
            "cleaned_data": {
                "company_number": company_details["company_number"],
                "name": company_details["name"],
                "readable_address": company_details["readable_address"],
                "companies_house": True,
            },
            "dirty_data": company_details_dirty_data,
        }
        self.request.session["businesses"] = current_businesses
        return super().form_valid(form)


class WhereIsTheBusinessLocatedView(BaseFormView):
    form_class = forms.WhereIsTheBusinessLocatedForm
    redirect_after_post = False

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        success_url = reverse("add_a_business", kwargs={"location": location, "business_uuid": self.kwargs["business_uuid"]})

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        return success_url
