import logging
from typing import Any, Dict

from apply_for_a_licence import choices
from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.forms import forms_business as forms
from apply_for_a_licence.models import Organisation
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.views.base_views import BaseSaveAndReturnFormView
from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)


class BaseBusinessModelFormView(AddAnEntityView):
    pk_url_kwarg = "business_id"
    model = Organisation
    context_object_name = "business"


class AddABusinessView(BaseBusinessModelFormView):
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

    def save_form(self, form):
        instance = form.save(commit=False)
        # the business should now be marked as 'complete'
        instance.status = choices.EntityStatusChoices.complete
        instance.save()
        return instance

    def get_success_url(self):
        success_url = reverse("business_added", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class BusinessAddedView(BaseSaveAndReturnFormView):
    form_class = forms.BusinessAddedForm
    template_name = "apply_for_a_licence/form_steps/business_added.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["licence_object"] = self.licence_object
        return kwargs

    def get_all_businesses(self) -> QuerySet[Organisation]:
        return Organisation.objects.filter(licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.business)

    def dispatch(self, request, *args, **kwargs):
        businesses = self.get_all_businesses()
        if len(businesses) > 0:
            # only allow access to this page if a business has been added
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(self.get_success_url())

    def get_success_url(self) -> str:
        try:
            add_business = self.form.cleaned_data["do_you_want_to_add_another_business"]
            if add_business:
                new_business = Organisation.objects.create(
                    licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.business
                )
                return (
                    reverse("is_the_business_registered_with_companies_house", kwargs={"licence_pk": self.kwargs["licence_pk"]})
                    + f"?business_id={new_business.id}"
                )
            else:
                return reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        except AttributeError:
            # No form object, send the user back to the tasklist to initiate the journey again
            return reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["businesses"] = self.get_all_businesses()
        return context


class DeleteBusinessView(DeleteAnEntityView):
    model = Organisation
    pk_url_kwarg = "business_id"

    def get_success_url(self):
        success_url = reverse("business_added", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class IsTheBusinessRegisteredWithCompaniesHouseView(BaseBusinessModelFormView):
    form_class = forms.IsTheBusinessRegisteredWithCompaniesHouseForm
    redirect_after_post = False
    redirect_with_query_parameters = True

    def get_business_id(self):
        if self.request.GET.get("new", ""):
            # The user wants to add a new business, create it now and assign the id
            # Lookup first to make sure there are no ghost ids
            new_business, created = Organisation.objects.get_or_create(
                licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.business, status="draft"
            )
            return new_business.id
        else:
            business_id = self.request.GET.get("business_id") or self.kwargs.get(self.pk_url_kwarg)
            if business_id:
                return int(business_id)
        return None

    def dispatch(self, request, *args, **kwargs):
        if business_id := self.get_business_id():
            self.kwargs[self.pk_url_kwarg] = business_id

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        answer = self.form.cleaned_data["business_registered_on_companies_house"]
        business_id = self.kwargs.get(self.pk_url_kwarg)
        if not business_id:
            raise ValueError("Missing business_id")
        if answer == "yes":
            success_url = reverse(
                "do_you_know_the_registered_company_number",
                kwargs={"licence_pk": self.kwargs["licence_pk"], "business_id": business_id},
            )
        else:
            success_url = reverse(
                "where_is_the_business_located", kwargs={"licence_pk": self.kwargs["licence_pk"], "business_id": business_id}
            )

        return success_url


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class DoYouKnowTheRegisteredCompanyNumberView(BaseBusinessModelFormView):
    form_class = forms.DoYouKnowTheRegisteredCompanyNumberForm
    template_name = "apply_for_a_licence/form_steps/conditional_radios_form.html"
    redirect_after_post = False
    redirect_with_query_parameters = True

    def get_success_url(self) -> str:
        do_you_know_the_registered_company_number = self.form.cleaned_data["do_you_know_the_registered_company_number"]
        registered_company_number = self.form.cleaned_data["registered_company_number"]
        if do_you_know_the_registered_company_number == "yes" and registered_company_number:
            if self.request.session.pop("company_details_500", None):
                success_url = reverse(
                    "manual_companies_house_input",
                    kwargs={"licence_pk": self.kwargs["licence_pk"], "business_id": self.kwargs.get("business_id")},
                )
            else:
                success_url = reverse(
                    "check_company_details",
                    kwargs={"licence_pk": self.kwargs["licence_pk"], "business_id": self.kwargs.get("business_id")},
                )
        else:
            success_url = reverse(
                "where_is_the_business_located",
                kwargs={"licence_pk": self.kwargs["licence_pk"], "business_id": self.kwargs.get("business_id")},
            )

        return success_url

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data()
        context["page_title"] = "Registered Company Number"
        return context

    def save_form(self, form) -> Organisation:
        instance = super().save_form(form)
        if form.cleaned_data["do_you_know_the_registered_company_number"] == "yes":
            instance.do_you_know_the_registered_company_number = True
        else:
            instance.do_you_know_the_registered_company_number = False

        instance.save()
        return instance


class ManualCompaniesHouseInputView(BaseBusinessModelFormView):
    form_class = forms.ManualCompaniesHouseInputForm
    template_name = "apply_for_a_licence/form_steps/manual_companies_house_input.html"

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        return reverse(
            "add_a_business",
            kwargs={"licence_pk": self.kwargs["licence_pk"], "location": location, "business_id": self.kwargs.get("business_id")},
        )


class CheckCompanyDetailsView(BaseBusinessModelFormView):
    template_name = "apply_for_a_licence/form_steps/check_company_details.html"
    form_class = forms.CheckCompanyDetailsForm

    def save_form(self, form):
        instance = super().save_form(form)
        instance.status = choices.EntityStatusChoices.complete
        instance.save()
        return instance

    def get_success_url(self):
        success_url = reverse("business_added", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class WhereIsTheBusinessLocatedView(BaseBusinessModelFormView):
    form_class = forms.WhereIsTheBusinessLocatedForm
    redirect_after_post = False
    pk_url_kwarg = "business_id"

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        success_url = reverse(
            "add_a_business",
            kwargs={"licence_pk": self.kwargs["licence_pk"], "location": location, "business_id": self.kwargs.get("business_id")},
        )
        return success_url

    def form_valid(self, form):
        if form.has_field_changed("where_is_the_address"):
            # if the field has changed, we need to clear the recipient address data
            form.instance.clear_address_data()
            form.instance.where_is_the_address = form.cleaned_data["where_is_the_address"]

        return super().form_valid(form)
