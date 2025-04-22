from typing import NoReturn

from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site
from django.contrib.auth.mixins import LoginRequiredMixin as DjangoLoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.urls import reverse


class LoginRequiredMixin(DjangoLoginRequiredMixin):
    def get_login_url(self) -> str:
        if is_apply_for_a_licence_site(self.request.site):
            # it's the public site, use GOV.UK One Login
            return reverse("authentication:login")
        elif is_view_a_licence_site(self.request.site):
            # it's the view-a-licence site, use Staff SSO
            return reverse("authbroker_client:login")
        raise Exception("unknown site", self.request.site)


class GroupsRequiredMixin:
    groups_required: list[str | None] = []

    def handle_no_group_membership(self, request: HttpRequest) -> NoReturn:
        raise PermissionDenied

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not request.user.is_authenticated:
            raise PermissionDenied
        else:
            if self.groups_required:
                user_groups = []
                for group in request.user.groups.values_list("name", flat=True):
                    user_groups.append(group)
                if len(set(user_groups).intersection(self.groups_required)) <= 0:
                    return self.handle_no_group_membership(request)
        return super().dispatch(request, *args, **kwargs)  # type: ignore
