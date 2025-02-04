import logging
import urllib.parse
import uuid
from typing import Any, Dict

from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.forms import forms_business as forms
from apply_for_a_licence.models import Organisation
from apply_for_a_licence.views.base_views import DeleteAnEntitySaveAndReturnView
from core.views.base_views import (
    BaseSaveAndReturnEntityModelFormView,
    BaseSaveAndReturnFormView,
)
from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)


class BaseBusinessModelFormView(BaseSaveAndReturnEntityModelFormView):
    pk_url_kwarg = "business_uuid"
    model = Organisation
    context_object_name = "business"


class AddABusinessView(BaseBusinessModelFormView):
    success_url = reverse_lazy("business_added")
    redirect_after_post = False

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_class(self):
        if self.location == "in-uk":
            form_class = forms.AddAUKBusinessForm
        else:
            form_class = forms.AddANonUKBusinessForm
        return form_class


class BusinessAddedView(BaseSaveAndReturnFormView):
    form_class = forms.BusinessAddedForm
    template_name = "apply_for_a_licence/form_steps/business_added.html"

    def get_all_objects(self) -> QuerySet[Organisation]:
        return Organisation.objects.filter(
            type_of_relationship=TypeOfRelationshipChoices.business,
            licence=self.licence_object,
        )

    def dispatch(self, request, *args, **kwargs):
        businesses = self.get_all_objects()
        if len(businesses) > 0:
            # only allow access to this page if a business has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("is_the_business_registered_with_companies_house", kwargs={"business_uuid": uuid.uuid4()})

    def get_success_url(self):
        add_business = self.form.cleaned_data["do_you_want_to_add_another_business"]
        if add_business:
            return (
                reverse("is_the_business_registered_with_companies_house", kwargs={"business_uuid": uuid.uuid4()}) + "?change=yes"
            )
        else:
            return reverse("previous_licence")

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["businesses"] = self.get_all_objects()
        return context


class DeleteBusinessView(DeleteAnEntitySaveAndReturnView):
    model = Organisation
    success_url = reverse_lazy("business_added")


class IsTheBusinessRegisteredWithCompaniesHouseView(BaseBusinessModelFormView):
    form_class = forms.IsTheBusinessRegisteredWithCompaniesHouseForm
    redirect_after_post = False

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get("business_uuid", ""):
            if not Organisation.objects.filter(pk=self.kwargs["business_uuid"]).exists():
                Organisation.objects.create(
                    pk=self.kwargs["business_uuid"],
                    licence=self.licence_object,
                    type_of_relationship=TypeOfRelationshipChoices.business,
                )
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["business_registered_on_companies_house"]
        if answer == "yes":
            success_url = reverse(
                "do_you_know_the_registered_company_number", kwargs={"business_uuid": self.kwargs.get("business_uuid")}
            )
        else:
            success_url = reverse("where_is_the_business_located", kwargs={"business_uuid": self.kwargs.get("business_uuid")})

        return success_url


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class DoYouKnowTheRegisteredCompanyNumberView(BaseBusinessModelFormView):
    form_class = forms.DoYouKnowTheRegisteredCompanyNumberForm
    template_name = "apply_for_a_licence/form_steps/conditional_radios_form.html"
    redirect_after_post = False

    def get_success_url(self) -> str:
        do_you_know_the_registered_company_number = self.form.cleaned_data["do_you_know_the_registered_company_number"]
        registered_company_number = self.form.cleaned_data["registered_company_number"]
        if do_you_know_the_registered_company_number == "yes" and registered_company_number:
            if self.request.session.pop("company_details_500", None):
                success_url = reverse("manual_companies_house_input", kwargs={"business_uuid": self.kwargs.get("business_uuid")})
            else:
                success_url = reverse("check_company_details", kwargs={"business_uuid": self.kwargs.get("business_uuid")})
        else:
            success_url = reverse("where_is_the_business_located", kwargs={"business_uuid": self.kwargs.get("business_uuid")})

        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters
        return success_url

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data()
        context["page_title"] = "Registered Company Number"
        return context


class ManualCompaniesHouseInputView(BaseBusinessModelFormView):
    form_class = forms.ManualCompaniesHouseInputForm
    template_name = "apply_for_a_licence/form_steps/manual_companies_house_input.html"

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["manual_companies_house_input"]
        return reverse("add_a_business", kwargs={"location": location, "business_uuid": self.kwargs.get("business_uuid")})


class CheckCompanyDetailsView(BaseBusinessModelFormView):
    template_name = "apply_for_a_licence/form_steps/check_company_details.html"
    success_url = reverse_lazy("business_added")
    form_class = forms.CheckCompanyDetailsForm


class WhereIsTheBusinessLocatedView(BaseBusinessModelFormView):
    form_class = forms.WhereIsTheBusinessLocatedForm
    redirect_after_post = False

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        success_url = reverse("add_a_business", kwargs={"location": location, "business_uuid": self.kwargs.get("business_uuid")})
        return success_url

    def form_valid(self, form):
        if form.has_field_changed("where_is_the_address"):
            # if the field has changed, we need to clear the recipient address data
            form.instance.clear_address_data()
            form.instance.where_is_the_address = form.cleaned_data["where_is_the_address"]

        return super().form_valid(form)
