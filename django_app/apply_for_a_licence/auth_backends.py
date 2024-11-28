from typing import TYPE_CHECKING, Any, Literal

from core.sites import is_view_a_licence_site
from django.contrib.auth import get_user_model
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

        user = super().authenticate(request, **credentials)
        if user:
            set_site_last_login(user, request.site)
        return user

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
