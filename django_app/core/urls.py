from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from .views import cookie_views

urlpatterns = [
    path("feedback/", include("feedback.urls")),
    path("pingdom/", include("healthcheck.urls")),
    path("throw_error/", lambda x: 1 / 0),
    path("admin/", admin.site.urls),
    path("apply-for-a-licence/", include("apply_for_a_licence.urls")),
    path("cookies_consent", cookie_views.CookiesConsentView.as_view(), name="cookies_consent"),
    path("hide_cookies", cookie_views.HideCookiesView.as_view(), name="hide_cookies"),
]

if settings.ENFORCE_STAFF_SSO:
    urlpatterns.append(
        path("auth/", include("authbroker_client.urls")),
    )

if settings.ENVIRONMENT == "local":
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
