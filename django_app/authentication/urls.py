from django.urls import path

from .views import AuthCallbackView, AuthView, LogoutView, SessionExpiredView

app_name = "authentication"
urlpatterns = [
    path("login/", AuthView.as_view(), name="login"),
    path("callback/", AuthCallbackView.as_view(), name="callback"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("session-expired/", SessionExpiredView.as_view(), name="session_expired"),
]
