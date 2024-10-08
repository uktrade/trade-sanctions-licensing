from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import cookie_views, generic_views
from .views.base_views import RedirectBaseDomainView

urlpatterns = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("feedback/", include("feedback.urls")),
    path("healthcheck/", include("healthcheck.urls")),
    path("throw_error/", lambda x: 1 / 0),
    path("admin/", admin.site.urls),
    path("apply/", include("apply_for_a_licence.urls")),
    path("view/", include("view_a_licence.urls")),
    path("cookies_consent", cookie_views.CookiesConsentView.as_view(), name="cookies_consent"),
    path("privacy-notice", generic_views.PrivacyNoticeView.as_view(), name="privacy_notice"),
    path("hide_cookies", cookie_views.HideCookiesView.as_view(), name="hide_cookies"),
    path("reset_session", generic_views.ResetSessionView.as_view(), name="reset_session"),
    path("accessibility-statement", generic_views.AccessibilityStatementView.as_view(), name="accessibility_statement"),
]

if settings.ENFORCE_STAFF_SSO:
    urlpatterns.append(
        path("auth/", include("authbroker_client.urls")),
    )

if settings.ENVIRONMENT == "local":
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
