from django.urls import path

from .views import AuthCallbackView, AuthView

app_name = "authentication"
urlpatterns = [
    path("login/", AuthView.as_view(), name="login"),
    path("callback/", AuthCallbackView.as_view(), name="callback"),
]
