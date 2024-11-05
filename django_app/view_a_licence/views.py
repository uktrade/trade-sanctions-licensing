import logging
from typing import Any

from apply_for_a_licence.models import Licence
from core.sites import require_view_a_licence
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, RedirectView, TemplateView

from .mixins import ActiveUserRequiredMixin, StaffUserOnlyMixin

logger = logging.getLogger(__name__)

# ALL VIEWS HERE MUST BE DECORATED WITH AT LEAST LoginRequiredMixin


@method_decorator(require_view_a_licence(), name="dispatch")
class RedirectBaseViewerView(LoginRequiredMixin, ActiveUserRequiredMixin, RedirectView):
    """Redirects view_a_licence base site visits to view-all-reports view"""

    @property
    def url(self) -> str:
        return reverse("view_a_licence:application_list")


@method_decorator(require_view_a_licence(), name="dispatch")
class ApplicationListView(LoginRequiredMixin, ActiveUserRequiredMixin, ListView):
    template_name = "view_a_licence/application_list.html"
    success_url = reverse_lazy("view_a_licence:application_list")
    model = Licence
    ordering = ["-created_at"]

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        self.request.session["sort"] = request.GET.get("sort_by", "newest")
        return super().get(request, **kwargs)

    def get_queryset(self) -> "QuerySet[Licence]":
        queryset = super().get_queryset()
        sort = self.request.session.get("sort", "newest")
        if sort == "oldest":
            queryset = reversed(queryset)
        return queryset

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["selected_sort"] = self.request.session.pop("sort", "newest")
        return context


@method_decorator(require_view_a_licence(), name="dispatch")
class ManageUsersView(LoginRequiredMixin, StaffUserOnlyMixin, TemplateView):
    template_name = "view_a_licence/manage_users.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pending_users"] = User.objects.filter(is_active=False, is_staff=False)
        context["accepted_users"] = User.objects.filter(is_active=True)
        return context

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        if update_user := self.request.GET.get("accept_user", None):
            user_to_accept = User.objects.get(id=update_user)
            user_to_accept.is_active = True
            user_to_accept.save()

            logger.info(
                f"{self.request.user} accepted user {user_to_accept.pk} - {user_to_accept.first_name} {user_to_accept.last_name}"
            )
            return HttpResponseRedirect(reverse("view_a_licence:manage_users"))

        if delete_user := self.request.GET.get("delete_user", None):
            denied_user = User.objects.get(id=delete_user)
            denied_user.delete()

            logger.info(f"{self.request.user} accepted user {denied_user.pk} - {denied_user.first_name} {denied_user.last_name}")
            return HttpResponseRedirect(reverse("view_a_licence:manage_users"))

        return super().get(request, **kwargs)


@method_decorator(require_view_a_licence(), name="dispatch")
class ViewALicenceApplicationView(LoginRequiredMixin, ActiveUserRequiredMixin, DetailView):
    template_name = "apply_for_a_licence/licence_application.html"
    context_object_name = "licence"
    model = Licence
    slug_url_kwarg = "reference"
    slug_field = "reference"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["back_button_text"] = "View all licence applications"
        return context
