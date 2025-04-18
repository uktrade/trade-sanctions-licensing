import logging
from typing import Any

from apply_for_a_licence.choices import (
    TypeOfRelationshipChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
)
from apply_for_a_licence.models import Licence
from authentication.mixins import LoginRequiredMixin
from core.sites import require_view_a_licence
from core.views.base_views import BaseDownloadPDFView
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, RedirectView, TemplateView
from feedback.models import FeedbackItem

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
    template_name = "view_a_licence/view_a_licence_application.html"
    context_object_name = "licence"
    model = Licence
    slug_url_kwarg = "reference"
    slug_field = "reference"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["back_button_text"] = "View all licence applications"

        if self.object.who_do_you_want_the_licence_to_cover == WhoDoYouWantTheLicenceToCoverChoices.individual.value:
            context["business_individuals_work_for"] = self.object.organisations.get(
                type_of_relationship=TypeOfRelationshipChoices.named_individuals
            )

        return context


@method_decorator(require_view_a_licence(), name="dispatch")
class ViewAllFeedbackView(LoginRequiredMixin, ActiveUserRequiredMixin, ListView):
    context_object_name = "feedback"
    model = FeedbackItem
    template_name = "view_a_licence/view_all_feedback.html"

    def get_queryset(self) -> "QuerySet[FeedbackItem]":
        queryset = super().get_queryset()
        if date_min := self.request.GET.get("date_min"):
            queryset = queryset.filter(created_at__date__gte=date_min)
        if date_max := self.request.GET.get("date_max"):
            queryset = queryset.filter(created_at__date__lte=date_max)
        return queryset


@method_decorator(require_view_a_licence(), name="dispatch")
class ViewFeedbackView(LoginRequiredMixin, ActiveUserRequiredMixin, DetailView):
    model = FeedbackItem
    template_name = "view_a_licence/view_feedback.html"
    context_object_name = "feedback"


@method_decorator(require_view_a_licence(), name="dispatch")
class DownloadPDFView(LoginRequiredMixin, ActiveUserRequiredMixin, BaseDownloadPDFView):
    template_name = "view_a_licence/view_application_pdf.html"
    header = "Apply for a licence to provide sanctioned trade services: application submitted "

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.reference = self.request.GET.get("reference", "")
        context["licence"] = Licence.objects.get(reference=self.reference)
        return context
