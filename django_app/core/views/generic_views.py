from core.utils import update_last_activity_session_timestamp
from django.conf import settings
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


class PingSessionView(View):
    """Pings the session to keep it alive"""

    def get(self, request: HttpRequest) -> HttpResponse:
        update_last_activity_session_timestamp(request)
        return HttpResponse("pong")


class SessionExpiredView(TemplateView):
    template_name = "core/session_expired.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        # the session should already be empty by definition but just in case, manually clear
        request.session.flush()
        return super().get(request, *args, **kwargs)
