from typing import Any

from authbroker_client.backends import AuthbrokerBackend
from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.http import HttpRequest

from .constants import ONE_LOGIN_UNSET_NAME
from .types import UserCreateData, UserInfo
from .utils import get_client, get_userinfo

UserModel = get_user_model()


class OneLoginBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, **credentials: Any) -> User | None:
        # GOV.UK One Login is only enabled on the apply-for-a-licence sites.
        if is_view_a_licence_site(request.site):
            return None

        client = get_client(request)

        if client.token:
            userinfo = get_userinfo(client)

            user = self.get_or_create_user(userinfo)
            return user

        return None

    def get_or_create_user(self, profile: UserInfo) -> User:
        """Get or create a user based on the OneLogin profile data."""

        one_login_user_id = profile["sub"]
        user_data: UserCreateData = {
            "email": profile["email"],
            "username": one_login_user_id,
            "first_name": ONE_LOGIN_UNSET_NAME,
            "last_name": ONE_LOGIN_UNSET_NAME,
            "is_active": True,
        }

        user, created = User.objects.get_or_create(username=one_login_user_id, defaults=user_data)

        if created:
            # if the user is created, set an unusable password
            user.set_unusable_password()
            user.save()
            public_user_group = Group.objects.get(name=settings.PUBLIC_USER_GROUP_NAME)
            user.groups.add(public_user_group)

        return user

    def get_user(self, user_id: int) -> User | None:
        """Get a user by the ID stored in their session"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class StaffSSOBackend(AuthbrokerBackend):
    def authenticate(self, request: HttpRequest, **credentials: Any) -> User | None:
        # GOV.UK One Login is only enabled on the apply-for-a-licence sites.
        if is_apply_for_a_licence_site(request.site):
            return None

        return super().authenticate(request, **credentials)

    def get_or_create_user(self, profile: dict[str, Any]) -> User:
        with transaction.atomic():
            try:
                if existing_user := User.objects.get(email=profile["email"]):
                    return existing_user
            except User.DoesNotExist:
                user_model = get_user_model()
                new_user = user_model.objects.create(
                    email=profile["email"],
                    first_name=profile["first_name"],
                    last_name=profile["last_name"],
                    username=profile["email_user_id"],
                    # the user is created as inactive and not staff, so they can be approved by staff members
                    is_active=False,
                    is_staff=False,
                )
                new_user.set_unusable_password()
                new_user.save()

                return new_user


class AdminBackend(ModelBackend):
    """Authentication backend only used on the admin site. Only enabled with DEBUG and INCLUDE_PRIVATE_URLS are True"""

    def authenticate(self, request, username: str | None = None, password: str | None = None, **kwargs) -> User | None:
        if settings.SHOW_ADMIN_PANEL:
            return super().authenticate(request, username, password, **kwargs)
        else:
            return None

    def user_can_authenticate(self, user):
        return user.is_staff and super().user_can_authenticate(user)
