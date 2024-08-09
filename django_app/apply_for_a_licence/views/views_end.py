import logging
from typing import Any

from apply_for_a_licence.utils import get_all_cleaned_data, get_all_forms
from core.document_storage import TemporaryDocumentStorage
from django.views.generic import TemplateView
from utils.s3 import get_all_session_files

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


class CompleteView(TemplateView):
    template_name = "apply_for_a_licence/complete.html"
