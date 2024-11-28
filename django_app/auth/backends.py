from typing import TYPE_CHECKING, Any, Literal

from authbroker_client.backends import AuthbrokerBackend
from core.sites import is_view_a_licence_site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest

from . import types
from .constants import ONE_LOGIN_UNSET_NAME

if TYPE_CHECKING:
    from django.contrib.auth.models import User

UserModel = get_user_model()


class OneLoginBackend:
    def authenticate(self, request: HttpRequest, **credentials: Any) -> User | None:
        # GOV.UK One Login is only enabled on the  sites.
        if is_view_a_licence_site(request.site):
            return None

        user = None
        client = get_client(request)

        if has_valid_token(client):
            userinfo = get_userinfo(client)

            user = self.get_or_create_user(userinfo)

        if user and self.user_can_authenticate(user):
            return user

        return None

    def get_or_create_user(self, profile: OneLoginUserInfo) -> User:
        id_key = self.get_profile_id_name()
        id_value = profile[id_key]
        user_data = self.user_create_mapping(profile)

        user, created = get_or_create_icms_user(id_value, user_data)
        return user

    def user_create_mapping(self, userinfo: types.UserInfo) -> types.UserCreateData:
        return {
            "email": userinfo["email"],
            "first_name": ONE_LOGIN_UNSET_NAME,
            "last_name": ONE_LOGIN_UNSET_NAME,
        }

    @staticmethod
    def get_profile_id_name() -> Literal["sub"]:
        return "sub"

    def get_user(self, user_id: int) -> "User | None":
        user_cls = get_user_model()

        try:
            return user_cls.objects.get(pk=user_id)

        except user_cls.DoesNotExist:
            return None

    def user_can_authenticate(self, user: "User") -> bool:
        """Reject users with is_active=False.

        Custom user models that don't have that attribute are allowed.
        """

        is_active = getattr(user, "is_active", None)

        return is_active or is_active is None


class StaffSSOBackend(AuthbrokerBackend):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

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
