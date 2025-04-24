from apply_for_a_licence.models import Licence
from apply_for_a_licence.tasklist import Tasklist
from apply_for_a_licence.utils import can_user_edit_licence
from core.views.base_views import BaseSaveAndReturnView, BaseView
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView


class TriageView(BaseView):
    """Triage view to take users to where they need to be.

    Checks that the licence belongs to them and that they can edit it. If so assign the PK to the session
    so that the user can continue to the tasklist and subsequent views."""

    def dispatch(self, request, *args, **kwargs):
        licence_object = get_object_or_404(Licence, pk=kwargs["licence_pk"])
        if can_user_edit_licence(request.user, licence_object):
            return redirect(reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]}))
        else:
            raise SuspiciousOperation("User does not have permission to edit this licence")


class TasklistView(BaseSaveAndReturnView, TemplateView):
    template_name = "apply_for_a_licence/tasklist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        licence = self.licence_object
        tasklist = Tasklist(licence).get_tasks()

        context["tasklist"] = tasklist
        context["licence"] = licence
        return context
