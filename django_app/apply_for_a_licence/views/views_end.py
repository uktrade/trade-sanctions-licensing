import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from apply_for_a_licence.forms.forms_end import DeclarationForm
from apply_for_a_licence.models import Document, Individual, Licence, Organisation
from authentication.mixins import LoginRequiredMixin
from core.document_storage import TemporaryDocumentStorage
from core.views.base_views import BaseFormView
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from utils.notifier import send_email
from utils.s3 import get_all_session_files
from view_a_licence.utils import get_view_a_licence_application_url

from django_app.utils.s3 import store_document_in_permanent_bucket

logger = logging.getLogger(__name__)


class CheckYourAnswersView(LoginRequiredMixin, TemplateView):
    """View for the 'Check your answers' page."""

    template_name = "apply_for_a_licence/form_steps/check_your_answers.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""

        context = super().get_context_data(**kwargs)
        #
        # TODO: Add kwarg
        #
        user_licence = Licence.objects.get(pk=kwargs["licence_id"])
        context["user_licence"] = user_licence
        context["business"] = Organisation.objects.get(licence=user_licence)
        context["individuals"] = Individual.objects.get(licence=user_licence)
        context["documents"] = Document.objects.filter(licence=user_licence)

        context["new_individual"] = str(uuid.uuid4())
        return context


@method_decorator(csrf_exempt, name="dispatch")
class DeclarationView(BaseFormView):
    form_class = DeclarationForm
    template_name = "apply_for_a_licence/form_steps/declaration.html"
    success_url = reverse_lazy("complete")

    def save_documents(self, licence_pk: str) -> None:
        #
        # TODO: Amend get_all_session_files
        #
        documents = get_all_session_files(TemporaryDocumentStorage(), self.request.session)
        for key, _ in documents.items():
            new_key = store_document_in_permanent_bucket(object_key=key, licence_pk=licence_pk)

            Document.objects.create(
                licence=self.licence_object,
                file=new_key,
            )

    def form_valid(self, form: DeclarationForm) -> HttpResponse:
        with transaction.atomic():

            licence_object = Licence.objects.get(pk=self.kwargs["licence_id"])
            datetime_now = datetime.now(timezone.utc)
            self.save_documents(licence_object)
            licence_object.submitted_at = datetime_now

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


class CompleteView(LoginRequiredMixin, TemplateView):
    template_name = "apply_for_a_licence/complete.html"
