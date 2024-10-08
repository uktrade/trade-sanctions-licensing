from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView


class ResetSessionView(View):
    """Resets and clears the users session"""

    def get(self, request: HttpRequest) -> HttpResponse:
        request.session.flush()
        return redirect("initial_redirect_view")


class PrivacyNoticeView(TemplateView):
    template_name = "core/privacy_notice.html"


class AccessibilityStatementView(TemplateView):
    template_name = "core/accessibility_statement.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["otsi_email"] = settings.OTSI_EMAIL
        return context
