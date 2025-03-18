from datetime import datetime

from authentication.mixins import GroupsRequiredMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render, reverse
from utils.notifier import send_email
from view_a_licence.utils import craft_view_a_licence_url


class InternalUserOnlyMixin(GroupsRequiredMixin):
    """Mixin to restrict access to internal users only (e.g. OTSI)"""

    groups_required = [settings.INTERNAL_USER_GROUP_NAME]

    def handle_no_group_membership(self, request):
        admin_url = craft_view_a_licence_url(reverse("view_a_licence:manage_users") + "#pending")
        user_login_datetime = f"{datetime.now():%Y-%m-%d %H:%M:%S%z}"
        for user in User.objects.filter(groups__name=settings.ADMIN_USER_GROUP_NAME):
            send_email(
                email=user.email,
                template_id=settings.NEW_OTSI_USER_TEMPLATE_ID,
                context={
                    "user_email": request.user.email,
                    "user_login_datetime": user_login_datetime,
                    "admin_url": admin_url,
                },
            )
        return render(request, "view_a_licence/unauthorised.html", status=403)


class AdminUserOnlyMixin(GroupsRequiredMixin):
    """Mixin to restrict access to admin users only"""

    groups_required = [settings.ADMIN_USER_GROUP_NAME]
