import logging
import uuid
from typing import Any

from apply_for_a_licence import choices
from apply_for_a_licence.forms.forms_end import DeclarationForm
from apply_for_a_licence.models import Individual, Organisation
from core.views.base_views import (
    BaseSaveAndReturnFormView,
    BaseSaveAndReturnView,
    BaseTemplateView,
)
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView
from utils.notifier import send_email
from view_a_licence.utils import get_view_a_licence_application_url

logger = logging.getLogger(__name__)


class CheckYourAnswersView(BaseSaveAndReturnView, TemplateView):
    """View for the 'Check your answers' page."""

    template_name = "apply_for_a_licence/form_steps/check_your_answers.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""
        context = super().get_context_data(**kwargs)
        licence = self.licence_object
        context["licence"] = licence
        context["recipients"] = licence.organisations.filter(type_of_relationship=choices.TypeOfRelationshipChoices.recipient)
        context["businesses"] = licence.organisations.filter(type_of_relationship=choices.TypeOfRelationshipChoices.business)
        context["individuals"] = licence.individuals.all()

        try:
            applicant_individual = licence.individuals.get(is_applicant=True)
            context["individuals"] = licence.individuals.exclude(pk=applicant_individual.pk)
            context["applicant_individual"] = applicant_individual
        except Individual.DoesNotExist:
            context["applicant_individual"] = None

        try:
            business_individual_works_for = licence.organisations.get(
                type_of_relationship=choices.TypeOfRelationshipChoices.named_individuals
            )
        except Organisation.DoesNotExist:
            business_individual_works_for = None
        context["business_individual_works_for"] = business_individual_works_for

        context["new_individual_uuid"] = str(uuid.uuid4())
        context["new_business_uuid"] = str(uuid.uuid4())
        return context


class DeclarationView(BaseSaveAndReturnFormView):
    form_class = DeclarationForm
    template_name = "apply_for_a_licence/form_steps/declaration.html"
    success_url = reverse_lazy("complete")

    def form_valid(self, form: DeclarationForm) -> HttpResponse:
        licence_object = self.licence_object

        licence_object.assign_reference()
        licence_object.status = choices.StatusChoices.submitted
        licence_object.submitted_at = timezone.now()
        licence_object.save()

        # Send confirmation email to the user
        send_email(
            email=licence_object.applicant_user_email_address,
            template_id=settings.PUBLIC_USER_NEW_APPLICATION_TEMPLATE_ID,
            context={"name": licence_object.applicant_full_name, "application_number": licence_object.reference},
        )

        # Send confirmation email to OTSI staff
        view_application_url = get_view_a_licence_application_url(licence_object.reference)

        for email in settings.NEW_APPLICATION_ALERT_RECIPIENTS:
            send_email(
                email=email,
                template_id=settings.OTSI_NEW_APPLICATION_TEMPLATE_ID,
                context={"application_number": licence_object.reference, "url": view_application_url},
            )

        # Successfully saved to DB - clear session ready for new application.
        # only do this if we're not in debug mode, sometimes nice to back and re-submit
        if not settings.DEBUG:
            self.request.session.flush()

        self.request.session["licence_reference"] = licence_object.reference
        self.request.session["applicant_email"] = licence_object.applicant_user_email_address

        return redirect(self.success_url)


class CompleteView(BaseTemplateView):
    template_name = "apply_for_a_licence/complete.html"
