from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import cookie_views, generic_views
from .views.base_views import RedirectBaseDomainView
from .views.generic_views import PingSessionView, SessionExpiredView
from .views.shared_views import DownloadPDFView

urlpatterns = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("feedback/", include("feedback.urls")),
    path("healthcheck/", include("healthcheck.urls")),
    path("throw_error/", lambda x: 1 / 0),
    path("admin/", admin.site.urls),
    path("apply/", include("apply_for_a_licence.urls")),
    path("view/", include("view_a_licence.urls")),
    path("cookies-policy", cookie_views.CookiesConsentView.as_view(), name="cookies_consent"),
    path("privacy-notice", generic_views.PrivacyNoticeView.as_view(), name="privacy_notice"),
    path("hide_cookies", cookie_views.HideCookiesView.as_view(), name="hide_cookies"),
    path("reset_session", generic_views.ResetSessionView.as_view(), name="reset_session"),
    path("ping_session/", PingSessionView.as_view(), name="ping_session"),
    path("inactive-application-deleted/", SessionExpiredView.as_view(), name="session_expired"),
    path("accessibility-statement", generic_views.AccessibilityStatementView.as_view(), name="accessibility_statement"),
    path("download_application/", DownloadPDFView.as_view(), name="download_application"),
    path("auth/", include("authbroker_client.urls")),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    # checking if we have debug_toolbar installed
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
