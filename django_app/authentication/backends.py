from typing import Any

from authbroker_client.backends import AuthbrokerBackend
from core.sites import is_view_a_licence_site
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest

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
        user_data: UserCreateData = settings.GOV_UK_ONE_LOGIN_CONFIG.get_user_create_mapping(profile)

        user, created = User.objects.get_or_create(username=one_login_user_id, defaults=user_data)

        if created:
            # if the user is created, set an unusable password
            user.set_unusable_password()
            user.save()

        return user

    def get_user(self, user_id: int) -> User | None:
        """Get a user by the ID stored in their session"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class StaffSSOBackend(AuthbrokerBackend):
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
                    is_active=False,
                    is_staff=False,
                )
                new_user.set_unusable_password()
                new_user.save()

                return new_user
