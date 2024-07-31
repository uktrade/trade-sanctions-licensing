import logging
import uuid
from typing import Any

from apply_for_a_licence.utils import get_all_cleaned_data, get_all_forms, get_form
from core.document_storage import TemporaryDocumentStorage
from core.utils import is_ajax
from core.views.base_views import BaseFormView
from django.conf import settings
from django.core.cache import cache
from django.forms import Form, ModelForm
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView, View
from django_ratelimit.decorators import ratelimit
from utils.notifier import verify_email
from utils.s3 import (
    generate_presigned_url,
    get_all_session_files,
    get_user_uploaded_files,
)

from . import forms
from .forms import DeclarationForm

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
        third_party_view = self.request.session.get("third_party", False)
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
        if start_view := self.request.session.get("start", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "business":
                return reverse("is_the_business_registered_with_companies_house")
            else:
                return reverse("add_an_individual")


class PreviousLicenceView(BaseFormView):
    form_class = forms.ExistingLicencesForm

    def get_success_url(self):
        success_url = reverse("type_of_service")
        if start_view := self.request.session.get("start", False):
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
    form_class = forms.IndividualAddedForm
    template_name = "apply_for_a_licence/form_steps/yourself_and_individual_added.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["yourself_form"] = get_form(self.request, "add_yourself")
        return context

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
    success_url = reverse_lazy("where_is_the_recipient_located")


class WhereIsTheRecipientLocatedView(BaseFormView):
    form_class = forms.WhereIsTheRecipientLocatedForm

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        return reverse("add_a_recipient", kwargs={"location": location})


class AddARecipientView(FormView):
    form_class = forms.AddARecipientForm
    template_name = "core/base_form_step.html"
    success_url = reverse_lazy("relationship_provider_recipient")

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # restore the form data from the recipient_uuid, if it exists
        if self.request.method == "GET":
            if recipient_uuid := self.request.GET.get("recipient_uuid", None):
                if recipient_dict := self.request.session.get("recipients", {}).get(recipient_uuid, None):
                    kwargs["data"] = recipient_dict["dirty_data"]
        if self.location == "in_the_uk":
            kwargs["is_uk_address"] = True
        return kwargs

    def form_valid(self, form: forms.AddARecipientForm) -> HttpResponse:
        current_recipients = self.request.session.get("recipients", {})
        # get the recipient_uuid if it exists, otherwise create it
        if recipient_uuid := self.request.GET.get("recipient_uuid", self.kwargs.get("recipient_uuid", str(uuid.uuid4()))):
            # used to display the recipient_uuid data in recipient_added.html
            current_recipients[recipient_uuid] = {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        self.request.session["recipients"] = current_recipients
        return super().form_valid(form)


class RecipientAddedView(BaseFormView):
    form_class = forms.RecipientAddedForm
    template_name = "apply_for_a_licence/form_steps/recipient_added.html"

    def get_success_url(self):
        add_recipient = self.form.cleaned_data["do_you_want_to_add_another_recipient"]
        if add_recipient:
            return reverse("where_is_the_recipient_located")
        else:
            return reverse("licensing_grounds")


class DeleteRecipientView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        recipients = self.request.session.get("recipients", [])
        # at least one recipient must be added
        if len(recipients) > 1:
            if recipients_uuid := self.request.POST.get("recipient_uuid"):
                recipients.pop(recipients_uuid, None)
                self.request.session["recipients"] = recipients
        return redirect(reverse_lazy("recipient_added"))


class RelationshipProviderRecipientView(BaseFormView):
    form_class = forms.RelationshipProviderRecipientForm
    success_url = reverse_lazy("recipient_added")


class LicensingGroundsView(BaseFormView):
    form_class = forms.LicensingGroundsForm
    success_url = reverse_lazy("purpose_of_provision")

    def get_success_url(self) -> str:

        if professional_or_business_service := self.request.session.get("ProfessionalOrBusinessServicesView", False):
            if professional_or_business_service.get("professional_or_business_service") == "legal_advisory":
                return reverse("licensing_grounds_legal_advisory")
        return reverse("purpose_of_provision")


class LicensingGroundsLegalAdvisoryView(BaseFormView):
    form_class = forms.LicensingGroundsForm
    success_url = reverse_lazy("upload_documents")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["legal_advisory"] = True
        return kwargs


class PurposeOfProvisionView(BaseFormView):
    form_class = forms.PurposeOfProvisionForm
    success_url = reverse_lazy("upload_documents")


class UploadDocumentsView(BaseFormView):
    """View for uploading documents.
    Accepts both Ajax and non-Ajax requests, to accommodate both JS and non-JS users respectively."""

    form_class = forms.UploadDocumentsForm
    template_name = "apply_for_a_licence/form_steps/upload_documents.html"
    file_storage = TemporaryDocumentStorage()

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Retrieve the already uploaded files from the session storage and add them to the context."""
        context = super().get_context_data(**kwargs)
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            context["session_files"] = session_files
        return context

    def form_valid(self, form: Form) -> HttpResponse:
        """Loop through the files and save them to the temporary storage. If the request is Ajax, return a JsonResponse.

        If the request is not Ajax, redirect to the summary page (the next step in the form)."""
        for temporary_file in form.cleaned_data["document"]:
            # adding the file name to the cache, so we can retrieve it later and confirm they uploaded it
            # we add a unique identifier to the key, so we do not overwrite previous uploads
            redis_cache_key = f"{self.request.session.session_key}{uuid.uuid4()}"
            cache.set(redis_cache_key, temporary_file.original_name)

            if is_ajax(self.request):
                # if it's an AJAX request, then files are sent to this view one at a time, so we can return a response
                # immediately, and not at the end of the for-loop
                return JsonResponse(
                    {
                        "success": True,
                        "file_name": temporary_file.original_name,
                    },
                    status=201,
                )
        if is_ajax(self.request):
            return JsonResponse({"success": True}, status=200)
        else:
            # todo redirect to summary
            return redirect(("declaration"))

    def form_invalid(self, form: Form) -> HttpResponse:
        if is_ajax(self.request):
            return JsonResponse(
                {"success": False, "error": form.errors["document"][0], "file_name": self.request.FILES["document"].name},
                status=200,
            )
        else:
            return super().form_invalid(form)


class DeleteDocumentsView(View):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        if file_name := self.request.GET.get("file_name"):
            full_file_path = f"{self.request.session.session_key}/{file_name}"
            TemporaryDocumentStorage().delete(full_file_path)
            if is_ajax(self.request):
                return JsonResponse({"success": True}, status=200)
            else:
                return redirect(reverse("upload_documents"))

        if is_ajax(self.request):
            return JsonResponse({"success": False}, status=400)
        else:
            return redirect(reverse("upload_documents"))


class DownloadDocumentView(View):
    http_method_names = ["get"]

    def get(self, *args: object, file_name, **kwargs: object) -> HttpResponse:
        user_uploaded_files = get_user_uploaded_files(self.request.session)

        if file_name in user_uploaded_files:
            logger.info(f"User is downloading file: {file_name}")
            session_keyed_file_name = f"{self.request.session.session_key}/{file_name}"
            file_url = generate_presigned_url(TemporaryDocumentStorage(), session_keyed_file_name)
            return redirect(file_url)

        raise Http404()


class CheckYourAnswersView(TemplateView):
    """View for the 'Check your answers' page."""

    template_name = "apply_for_a_licence/form_steps/check_your_answers.html"
    success_url = reverse_lazy("declaration")

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""
        forms = get_all_forms(self.request)
        context = super().get_context_data(**kwargs)
        all_cleaned_data = get_all_cleaned_data(self.request)
        print(forms["licensing_grounds"].get_licensing_grounds_display())
        context["form_data"] = all_cleaned_data
        context["forms"] = get_all_forms(self.request)
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            context["session_files"] = session_files
        if businesses := self.request.session.get("businesses", None):
            context["businesses"] = businesses
        if individuals := self.request.session.get("individuals", None):
            context["individuals"] = individuals

        if recipients := self.request.session.get("recipients", None):
            context["recipients"] = recipients
        return context


class DeclarationView(BaseFormView):
    form_class = forms.DeclarationForm
    template_name = "apply_for_a_licence/form_steps/declaration.html"
    success_url = reverse_lazy("complete")

    def form_valid(self, form: DeclarationForm) -> HttpResponse:
        all_forms = get_all_forms(self.request)
        for form in all_forms.values():
            if isinstance(form, ModelForm):
                form.save()
            elif isinstance(form, Form):
                print(form)
            else:
                continue
