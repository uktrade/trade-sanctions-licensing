from django.urls import path

from . import views

app_name = "view_a_licence"

urlpatterns = [
    path("", views.ApplicationListView.as_view(), name="application_list"),
    path("view/<int:pk>/", views.ViewALicenceApplicationView.as_view(), name="view_application"),
    path("manage_users/", views.ManageUsersView.as_view(), name="manage_users"),
]
