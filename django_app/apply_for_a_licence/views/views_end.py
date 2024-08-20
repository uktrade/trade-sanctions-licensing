import logging
from typing import Any

from apply_for_a_licence.forms.forms_yourself import DeclarationForm
from apply_for_a_licence.models import (
    Applicant,
    Document,
    Individual,
    Licence,
    Organisation,
)
from apply_for_a_licence.utils import get_all_cleaned_data, get_all_forms
from core.document_storage import TemporaryDocumentStorage
from core.views.base_views import BaseFormView
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from utils.s3 import get_all_session_files
from utils.save_to_db import SaveToDB

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
        if businesses := self.request.session.get("businesses", None):
            context["businesses"] = businesses
        if individuals := self.request.session.get("individuals", None):
            context["individuals"] = individuals

        if recipients := self.request.session.get("recipients", None):
            context["recipients"] = recipients
        return context


class DeclarationView(BaseFormView):
    form_class = DeclarationForm
    template_name = "apply_for_a_licence/form_steps/declaration.html"
    success_url = reverse_lazy("complete")

    def form_valid(self, form: DeclarationForm) -> HttpResponse:
        cleaned_data = get_all_cleaned_data(self.request)
        licence_object = Licence.objects
        applicant_object = Applicant.objects
        individual = None
        is_individual = False
        is_on_companies_house = False
        is_third_party = False
        business_employing_individual = None

        if cleaned_data["start"]["who_do_you_want_the_licence_to_cover"] in ["myself", "individual"]:
            is_individual = True
            individual = Individual.objects
            if cleaned_data["start"]["who_do_you_want_the_licence_to_cover"] == "individual":
                business_employing_individual = Organisation.objects

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
                licence=licence_object,
                applicant=applicant_object,
                data=cleaned_data,
                is_individual=is_individual,
                is_on_companies_house=is_on_companies_house,
                is_third_party=is_third_party,
            )

            # order is important
            # TODO: When the bugfixes are resolved we will have to loop for individuals, businesses, recipients
            # There will only be one applicant per licence,
            # but there may be several individuals/recipients/businesses per licence
            applicant_instance = save_object.save_applicant()
            save_object.save_licence(applicant_instance)
            if is_individual:
                save_object.save_individual(individual)
                if business_employing_individual is not None:
                    save_object.save_business(business_employing_individual)
            else:
                save_object.save_business(Organisation.objects)

            save_object.save_recipient(Organisation.objects)

            if cleaned_data["upload_documents"]["document"]:
                save_object.save_document(Document.objects)

        return redirect(self.success_url)


class CompleteView(TemplateView):
    template_name = "apply_for_a_licence/complete.html"
