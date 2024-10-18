import logging
import uuid
from typing import Any

from apply_for_a_licence.forms.forms_end import DeclarationForm
from apply_for_a_licence.utils import get_all_cleaned_data, get_all_forms
from core.document_storage import TemporaryDocumentStorage
from core.views.base_views import BaseFormView
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from utils.notifier import send_email
from utils.s3 import get_all_session_files
from utils.save_to_db import SaveToDB
from view_a_licence.utils import craft_view_a_licence_url

logger = logging.getLogger(__name__)


class CheckYourAnswersView(TemplateView):
    """View for the 'Check your answers' page."""

    template_name = "apply_for_a_licence/form_steps/check_your_answers.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""
        context = super().get_context_data(**kwargs)
        all_cleaned_data = get_all_cleaned_data(self.request)
        all_forms = get_all_forms(self.request)
        context["form_data"] = all_cleaned_data
        context["forms"] = all_forms
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            context["session_files"] = session_files

        if user_location := self.request.session.get("add_yourself_address", {}).get("country", ""):
            context["add_yourself_address"] = "in-uk" if user_location == "GB" else "outside-uk"

        if businesses := self.request.session.get("businesses", None):
            context["businesses"] = businesses
        if individuals := self.request.session.get("individuals", None):
            context["individuals"] = individuals
        if recipients := self.request.session.get("recipients", None):
            context["recipients"] = recipients

        context["new_individual"] = str(uuid.uuid4())
        return context


@method_decorator(csrf_exempt, name="dispatch")
class DeclarationView(BaseFormView):
    form_class = DeclarationForm
    template_name = "apply_for_a_licence/form_steps/declaration.html"
    success_url = reverse_lazy("complete")

    def form_valid(self, form: DeclarationForm) -> HttpResponse:
        cleaned_data = get_all_cleaned_data(self.request)
        is_myself = False
        is_individual = False
        is_on_companies_house = False
        is_third_party = False
        business_employing_individual = False

        if cleaned_data["start"]["who_do_you_want_the_licence_to_cover"] == "myself":
            is_myself = True
            cleaned_data["add_yourself_address"] = self.request.session["add_yourself_address"]
        elif cleaned_data["start"]["who_do_you_want_the_licence_to_cover"] == "individual":
            is_individual = True
            business_employing_individual = True

        if (
            cleaned_data["is_the_business_registered_with_companies_house"].get("business_registered_on_companies_house", "")
            == "yes"
            and cleaned_data["do_you_know_the_registered_company_number"].get("do_you_know_the_registered_company_number", "")
            == "yes"
        ):
            is_on_companies_house = True

        if cleaned_data["are_you_third_party"].get("are_you_applying_on_behalf_of_someone_else", ""):
            is_third_party = True

        with transaction.atomic():
            save_object = SaveToDB(
                self.request,
                data=cleaned_data,
                is_individual=is_individual,
                is_on_companies_house=is_on_companies_house,
                is_third_party=is_third_party,
            )

            new_licence_object = save_object.save_licence()

            if is_myself or is_individual:
                save_object.save_individuals()
                if business_employing_individual:
                    save_object.save_business()

            else:
                save_object.save_business()

            save_object.save_recipient()

            # moving the uploaded documents to permanent storage
            save_object.save_documents()

        # Send confirmation email to the user
        send_email(
            email=new_licence_object.applicant_user_email_address,
            template_id=settings.PUBLIC_USER_NEW_APPLICATION_TEMPLATE_ID,
            context={"name": new_licence_object.applicant_full_name, "application_number": new_licence_object.reference},
        )

        # Send confirmation email to OTSI staff
        view_application_url = craft_view_a_licence_url(
            reverse("view_a_licence:view_application", kwargs={"pk": new_licence_object.pk})
        )
        for email in settings.NEW_APPLICATION_ALERT_RECIPIENTS:
            send_email(
                email=email,
                template_id=settings.OTSI_NEW_APPLICATION_TEMPLATE_ID,
                context={"application_number": new_licence_object.reference, "url": view_application_url},
            )
            # Successfully saved to DB - clear session ready for new application
            self.request.session.flush()

        self.request.session["licence_reference"] = new_licence_object.reference
        self.request.session["applicant_email"] = new_licence_object.applicant_user_email_address

        return redirect(self.success_url)


class CompleteView(TemplateView):
    template_name = "apply_for_a_licence/complete.html"
