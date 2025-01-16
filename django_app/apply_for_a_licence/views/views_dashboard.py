from apply_for_a_licence.choices import StatusChoices
from core.views.base_views import BaseTemplateView
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.detail import DetailView


class DashboardView(BaseTemplateView):
    template_name = "apply_for_a_licence/dashboard/dashboard.html"

    def get(self, *args, **kwargs):
        self.applications = self.request.user.licence_applications.order_by("-created_at")
        if self.applications.count() == 0:
            # if we're here, the user has no applications, so redirect them to start a new one
            return redirect(reverse("new_application"))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["applications"] = self.applications
        return context


class NewApplicationView(BaseTemplateView):
    template_name = "apply_for_a_licence/dashboard/start_a_new_application.html"


class DeleteApplicationView(DetailView):
    template_name = "apply_for_a_licence/dashboard/delete_application.html"
    context_object_name = "application"

    def get_queryset(self):
        return self.request.user.licence_applications.filter(status=StatusChoices.draft)

    def post(self, *args, **kwargs):
        self.get_object().delete()
        return redirect(reverse("dashboard"))
