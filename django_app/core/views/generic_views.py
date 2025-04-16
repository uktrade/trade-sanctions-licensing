from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site
from core.utils import update_last_activity_session_timestamp
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import RedirectView, TemplateView


class ResetSessionView(View):
    """Resets and clears the users session"""

    def get(self, request: HttpRequest) -> HttpResponse:
        request.session.flush()
        return redirect("initial_redirect_view")


class PrivacyNoticeView(TemplateView):
    template_name = "core/privacy_notice.html"


class AccessibilityStatementView(TemplateView):
    template_name = "core/accessibility_statement.html"


class HelpAndSupportView(TemplateView):
    template_name = "core/help_and_support.html"


class PingSessionView(View):
    """Pings the session to keep it alive"""

    def get(self, request: HttpRequest) -> HttpResponse:
        update_last_activity_session_timestamp(request)
        return HttpResponse("pong")


class RedirectBaseDomainView(RedirectView):
    """Redirects base url visits to either apply-for-a-licence or view-a-licence default view"""

    @property
    def url(self) -> str:
        if is_apply_for_a_licence_site(self.request.site):
            return reverse("dashboard")
        elif is_view_a_licence_site(self.request.site):
            return reverse("view_a_licence:application_list")
        return ""
