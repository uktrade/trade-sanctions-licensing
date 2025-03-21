import logging

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import cookie_views, generic_views
from .views.base_views import RedirectBaseDomainView
from .views.generic_views import PingSessionView, SessionExpiredView

public_urls = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("give-feedback/", include("feedback.urls")),
    path("healthcheck/", include("healthcheck.urls")),
    path("throw_error/", lambda x: 1 / 0),
    path("apply/", include("apply_for_a_licence.urls")),
    path("cookies-policy", cookie_views.CookiesConsentView.as_view(), name="cookies_consent"),
    path("privacy-notice", generic_views.PrivacyNoticeView.as_view(), name="privacy_notice"),
    path("hide_cookies", cookie_views.HideCookiesView.as_view(), name="hide_cookies"),
    path("reset_session", generic_views.ResetSessionView.as_view(), name="reset_session"),
    path("ping_session/", PingSessionView.as_view(), name="ping_session"),
    path("inactive-application-deleted/", SessionExpiredView.as_view(), name="session_expired"),
    path("accessibility-statement", generic_views.AccessibilityStatementView.as_view(), name="accessibility_statement"),
    path("help-support", generic_views.HelpAndSupportView.as_view(), name="help_and_support"),
    path("staff-sso/", include("authbroker_client.urls")),
    path("authentication/", include("authentication.urls")),
]

private_urls = [
    path("view/", include("view_a_licence.urls")),
]

if settings.SHOW_ADMIN_PANEL:
    private_urls.append(path("admin/", admin.site.urls))

if settings.INCLUDE_PRIVATE_URLS:
    logging.info("Include private urls")
    urlpatterns = public_urls + private_urls
else:
    logging.info("Excluding private urls")
    urlpatterns = public_urls

if "debug_toolbar" in settings.INSTALLED_APPS:
    # checking if we have debug_toolbar installed
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
