from django.urls import path

from . import views

app_name = "view_a_licence"

urlpatterns = [
    path("", views.RedirectBaseViewerView.as_view(), name="initial_redirect_view"),
    path("view-all-applications", views.ApplicationListView.as_view(), name="application_list"),
    path("view-application/<str:reference>/", views.ViewALicenceApplicationView.as_view(), name="view_application"),
    path("manage-users/", views.ManageUsersView.as_view(), name="manage_users"),
]
