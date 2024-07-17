import logging
import uuid
from typing import Any

from core.views.base_views import BaseFormView
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView
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
    success_url = reverse_lazy("what_is_your_email")


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

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if form_h1_header := getattr(forms.WhatIsYourEmailForm, "form_h1_header"):
            context["form_h1_header"] = form_h1_header
        return context

    def get_success_url(self) -> str:
        start_view = self.request.session.get("StartView", False)
        third_party_view = self.request.session.get("ThirdPartyView", False)
        if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
            return reverse("add_yourself")
        elif third_party_view.get("are_you_applying_on_behalf_of_someone_else") == "True":
            return reverse("your_details")
        elif start_view.get("who_do_you_want_the_licence_to_cover") == "business":
            return reverse("is_the_business_registered_with_companies_house")
        else:
            return reverse("add_an_individual")


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
        if start_view := self.request.session.get("StartView", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "business":
                return reverse("is_the_business_registered_with_companies_house")
            else:
                return reverse("add_an_individual")


class PreviousLicenceView(BaseFormView):
    form_class = forms.ExistingLicencesForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def get_success_url(self):
        success_url = reverse("type_of_service")
        if start_view := self.request.session.get("StartView", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                success_url = reverse("business_employing_individual")
        return success_url


class BusinessEmployingIndividualView(BaseFormView):
    form_class = forms.BusinessEmployingIndividualForm
    success_url = reverse_lazy("type_of_service")


class AddABusinessView(FormView):
    form_class = forms.AddABusinessForm
    template_name = "core/base_form_step.html"
    success_url = reverse_lazy("business_added")

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # restore the form data from the business_uuid, if it exists
        if self.request.method == "GET":
            if business_uuid := self.request.GET.get("business_uuid", None):
                if businesses_dict := self.request.session.get("businesses", {}).get(business_uuid, None):
                    kwargs["data"] = businesses_dict["dirty_data"]
            if self.location == "in_the_uk":
                kwargs["is_uk_address"] = True
        return kwargs

    def form_valid(self, form: forms.AddABusinessForm) -> HttpResponse:
        current_businesses = self.request.session.get("businesses", {})
        # get the business_uuid if it exists, otherwise create it
        if business_uuid := self.request.GET.get("business_uuid", self.kwargs.get("business_uuid", str(uuid.uuid4()))):
            # used to display the business_uuid data in business_added.html
            current_businesses[business_uuid] = {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        self.request.session["businesses"] = current_businesses
        self.request.session.modified = True
        return super().form_valid(form)


class BusinessAddedView(BaseFormView):
    form_class = forms.BusinessAddedForm
    template_name = "apply_for_a_licence/form_steps/business_added.html"

    def dispatch(self, request, *args, **kwargs):
        if len(request.session.get("businesses", [])) >= 1:
            return super().dispatch(request, *args, **kwargs)
        return redirect("is_the_business_registered_with_companies_house")

    def get_success_url(self):
        add_business = self.form.cleaned_data["do_you_want_to_add_another_business"]
        if add_business:
            return reverse("is_the_business_registered_with_companies_house")
        else:
            return reverse("previous_licence")


class DeleteBusinessView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        businesses = self.request.session.get("businesses", [])
        # at least one business must be added
        if len(businesses) > 1:
            if business_uuid := self.request.POST.get("business_uuid"):
                businesses.pop(business_uuid, None)
                self.request.session["businesses"] = businesses
                self.request.session.modified = True
        return redirect(reverse_lazy("business_added"))


class AddAnIndividualView(FormView):
    form_class = forms.AddAnIndividualForm
    template_name = "core/base_form_step.html"

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
        self.request.session.modified = True
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse("individual_added")
        if start_view := self.request.session.get("StartView", False):
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
                self.request.session.modified = True
        return redirect(reverse_lazy("individual_added"))


class AddYourselfView(BaseFormView):
    form_class = forms.AddYourselfForm
    success_url = reverse_lazy("add_yourself_address")

    def form_valid(self, form: forms.AddYourselfAddressForm) -> HttpResponse:
        cleaned_data = form.cleaned_data
        cleaned_data["nationality_and_location"] = dict(form.fields["nationality_and_location"].choices)[
            form.cleaned_data["nationality_and_location"]
        ]
        add_yourself = {
            "cleaned_data": cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["add_yourself"] = add_yourself
        self.request.session.modified = True
        return super().form_valid(form)


class AddYourselfAddressView(BaseFormView):
    form_class = forms.AddYourselfAddressForm
    success_url = reverse_lazy("yourself_and_individual_added")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if add_yourself_view := self.request.session.get("AddYourselfView", False):
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
        self.request.session.modified = True
        return super().form_valid(form)


class YourselfAndIndividualAddedView(BaseFormView):
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/yourself_and_individual_added.html"

    def get_success_url(self):
        add_individual = self.form.cleaned_data["do_you_want_to_add_another_individual"]
        if add_individual:
            return reverse("add_an_individual")
        else:
            return reverse("previous_licence")


class DeleteIndividualFromYourselfView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        redirect_to = redirect(reverse_lazy("yourself_and_individual_added"))
        if individual_uuid := self.request.POST.get("individual_uuid"):
            individuals = self.request.session.get("individuals", None)
            individuals.pop(individual_uuid, None)
            self.request.session["individuals"] = individuals
            self.request.session.modified = True
        return redirect_to


class IsTheBusinessRegisteredWithCompaniesHouseView(BaseFormView):
    form_class = forms.IsTheBusinessRegisteredWithCompaniesHouseForm

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["business_registered_on_companies_house"]

        if answer == "yes":
            return reverse("do_you_know_the_registered_company_number")
        else:
            return reverse("where_is_the_business_located")


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class DoYouKnowTheRegisteredCompanyNumberView(BaseFormView):
    form_class = forms.DoYouKnowTheRegisteredCompanyNumberForm

    def __init__(self):
        self.business_uuid = None

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super(DoYouKnowTheRegisteredCompanyNumberView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form: forms.AddABusinessForm) -> HttpResponse:
        # Want to add companies house businesses to the business list
        current_businesses = self.request.session.get("businesses", {})
        # get the business_uuid if it exists, otherwise create it
        self.business_uuid = self.request.GET.get("business_uuid", self.kwargs.get("business_uuid", str(uuid.uuid4())))
        # used to display the business_uuid data in business_added.html

        current_businesses[self.business_uuid] = {
            "cleaned_data": {
                "company_number": form.cleaned_data["registered_company_number"],
                "name": form.cleaned_data["registered_company_name"],
                "readable_address": form.cleaned_data["registered_office_address"],
                "companies_house": True,
            },
            "dirty_data": form.data,
        }
        self.request.session["businesses"] = current_businesses
        self.request.session.modified = True
        return super().form_valid(form)

    def get_success_url(self) -> str:
        success_url = reverse("where_is_the_business_located")
        do_you_know_the_registered_company_number = self.form.cleaned_data["do_you_know_the_registered_company_number"]
        registered_company_number = self.form.cleaned_data["registered_company_number"]
        if do_you_know_the_registered_company_number == "yes" and registered_company_number:
            if self.request.session.get("company_details_500"):
                success_url = reverse("manual_companies_house_input")
            else:
                success_url = reverse("check_company_details", kwargs={"business_uuid": self.business_uuid})
        return success_url


class ManualCompaniesHouseInputView(BaseFormView):
    form_class = forms.ManualCompaniesHouseInputForm
    template_name = "apply_for_a_licence/form_steps/manual_companies_house_input.html"

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["manual_companies_house_input"]
        return reverse("add_a_business", kwargs={"location": location})


class CheckCompanyDetailsView(BaseFormView):
    template_name = "apply_for_a_licence/form_steps/check_company_details.html"
    form_class = forms.BaseForm
    success_url = reverse_lazy("business_added")


class WhereIsTheBusinessLocatedView(BaseFormView):
    form_class = forms.WhereIsTheBusinessLocatedForm

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        return reverse("add_a_business", kwargs={"location": location})


class TypeOfServiceView(BaseFormView):
    form_class = forms.TypeOfServiceForm

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["type_of_service"]
        match answer:
            case "interception_or_monitoring":
                success_url = reverse("which_sanctions_regime")
            case "internet":
                success_url = reverse("which_sanctions_regime")
            case "professional_and_business":
                success_url = reverse("professional_or_business_services")
            case _:
                success_url = reverse("service_activities")
        return success_url


class ProfessionalOrBusinessServicesView(BaseFormView):
    form_class = forms.ProfessionalOrBusinessServicesForm
    success_url = reverse_lazy("service_activities")


class WhichSanctionsRegimeView(BaseFormView):
    form_class = forms.WhichSanctionsRegimeForm
    success_url = reverse_lazy("service_activities")


class ServiceActivitiesView(BaseFormView):
    form_class = forms.ServiceActivitiesForm
    # todo: change success url to recipients flow
    success_url = reverse_lazy("complete")


class LicensingGroundsView(BaseFormView):
    form_class = forms.LicensingGroundsForm
    success_url = reverse_lazy("purpose_of_provision")


class PurposeOfProvisionView(BaseFormView):
    form_class = forms.PurposeOfProvisionForm
    # todo: change success url to upload documents
    success_url = reverse_lazy("complete")
