from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site
from core.utils import update_last_activity_session_timestamp
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import RedirectView, TemplateView
from django_ratelimit.exceptions import Ratelimited


class ResetSessionView(View):
    """Resets and clears the users session"""

    def get(self, request: HttpRequest) -> HttpResponse:
        request.session.flush()
        return redirect("initial_redirect_view")


class PrivacyNoticeView(TemplateView):
    template_name = "core/privacy_notice.html"


class AccessibilityStatementView(TemplateView):
    template_name = "core/accessibility_statement.html"


class PingSessionView(View):
    """Pings the session to keep it alive"""

    def get(self, request: HttpRequest) -> HttpResponse:
        update_last_activity_session_timestamp(request)
        return HttpResponse("pong")


class SessionExpiredView(TemplateView):
    template_name = "core/session_expired.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        logout(request)

        gov_one_logout_url = "https://oidc.integration.account.gov.uk/logout"
        post_logout_redirect_url = request.build_absolute_uri(reverse("session-expired"))

        if oidc_id_token := request.session.get("oidc_id_token", None):
            gov_one_logout_url += f"?id_token_hint={oidc_id_token}&post_logout_redirect_uri={post_logout_redirect_url}"

        super().get_context_data(**kwargs)

        return HttpResponseRedirect(gov_one_logout_url)


def rate_limited_view(request: HttpRequest, exception: Ratelimited) -> HttpResponse:
    return HttpResponse("You have made too many", status=429)


class RedirectBaseDomainView(RedirectView):
    """Redirects base url visits to either apply-for-a-licence or view-a-licence default view"""

    @property
    def url(self) -> str:
        if is_apply_for_a_licence_site(self.request.site):
            return reverse("dashboard")
        elif is_view_a_licence_site(self.request.site):
            return reverse("view_a_licence:application_list")
        return ""
