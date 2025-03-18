from apply_for_a_licence.choices import StatusChoices
from authentication.mixins import LoginRequiredMixin
from core.decorators import reset_last_activity_session_timestamp
from core.views.base_views import BaseTemplateView
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView


class DashboardView(BaseTemplateView):
    template_name = "apply_for_a_licence/dashboard/dashboard.html"

    def get(self, *args, **kwargs):
        self.applications = self.request.user.licence_applications.order_by("-created_at")

        if self.applications.count() == 0:
            # if we're here, the user has no applications, so redirect them to start a new one
            return redirect(reverse("new_application"))
        else:
            # let's go through the applications and see if any are over the 28-day limit, if so delete them
            # we might as well do this here rather than create a complex cron job or management command
            for application in self.applications:
                if application.is_expired():
                    # "pop" the application from the queryset
                    self.applications = self.applications.exclude(id=application.id)
                    application.delete()

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["id_token"] = self.request.session["_one_login_token"]["id_token"]
        context["applications"] = self.applications
        context["DRAFT_APPLICATION_EXPIRY_DAYS"] = settings.DRAFT_APPLICATION_EXPIRY_DAYS
        return context


@method_decorator(reset_last_activity_session_timestamp, name="dispatch")
class NewApplicationView(BaseTemplateView):
    template_name = "apply_for_a_licence/dashboard/start_a_new_application.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["id_token"] = self.request.session["_one_login_token"]["id_token"]
        context["DRAFT_APPLICATION_EXPIRY_DAYS"] = settings.DRAFT_APPLICATION_EXPIRY_DAYS
        return context


class DeleteApplicationView(LoginRequiredMixin, DetailView):
    template_name = "apply_for_a_licence/dashboard/delete_application.html"
    context_object_name = "application"

    def get_queryset(self):
        return self.request.user.licence_applications.filter(status=StatusChoices.draft)

    def post(self, *args, **kwargs):
        self.get_object().delete()
        return redirect(reverse("dashboard"))
