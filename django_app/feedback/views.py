import logging

from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from .forms import FeedbackForm

logger = logging.getLogger(__name__)


class ProvideFullFeedbackView(FormView):
    """View for collecting full feedback from the user."""

    form_class = FeedbackForm
    template_name = "feedback/collect_feedback.html"

    def form_valid(self, form: FeedbackForm) -> HttpResponseRedirect:
        feedback_item = form.save()

        # adding the URL to the new feedback item
        if url := self.request.GET.get("url"):
            feedback_item.url = url
            feedback_item.save()

        return redirect("feedback:feedback_done")

    def form_invalid(self, form):
        logger.error("Feedback form is invalid", extra={"form_errors": form.errors})
        return super().form_invalid(form)


class FeedbackDoneView(TemplateView):
    template_name = "feedback/feedback_done.html"
