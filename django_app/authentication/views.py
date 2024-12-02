import logging
from typing import Any

from authlib.common.security import generate_token
from authlib.jose.errors import InvalidClaimError
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic.base import RedirectView, View

from .constants import AUTHENTICATION_LEVEL, CONFIDENCE_LEVEL
from .utils import TOKEN_SESSION_KEY, get_client, get_token

logger = logging.getLogger(__name__)


def get_trust_vector(auth_level: str, identity_level: str) -> dict[str, str]:
    return {"vtr": f"['{auth_level}.{identity_level}']"}


REDIRECT_SESSION_FIELD_NAME = f"_oauth2_{REDIRECT_FIELD_NAME}"


def get_next_url(request):
    """Copied straight from staff-sso-client.

    https://github.com/uktrade/django-staff-sso-client/blob/master/authbroker_client/views.py
    """
    next_url = request.GET.get(REDIRECT_FIELD_NAME, request.session.get(REDIRECT_SESSION_FIELD_NAME))
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts=settings.ALLOWED_HOSTS, require_https=request.is_secure()
    ):
        return next_url

    return None


class AuthView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        client = get_client(self.request)
        config = settings.GOV_UK_ONE_LOGIN_CONFIG()

        nonce = generate_token()
        trust_vector = get_trust_vector(
            AUTHENTICATION_LEVEL,
            CONFIDENCE_LEVEL,
        )

        # create the /authorize URL with the correct parameters
        url, state = client.create_authorization_url(
            config.authorise_url,
            nonce=nonce,
            **trust_vector,
        )

        # storing state and nonce in session
        self.request.session[REDIRECT_SESSION_FIELD_NAME] = get_next_url(self.request)
        self.request.session[f"{TOKEN_SESSION_KEY}_oauth_state"] = state
        self.request.session[f"{TOKEN_SESSION_KEY}_oauth_nonce"] = nonce

        return url


class AuthCallbackView(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        auth_code = self.request.GET.get("code", None)

        if not auth_code:
            logger.error("No auth code returned from one_login")
            return redirect(reverse("login-start"))

        if state := request.session.get(f"{TOKEN_SESSION_KEY}_oauth_state", None):
            auth_service_state = self.request.GET.get("state")
            if state != auth_service_state:
                logger.error("Session state and passed back state differ")
                raise SuspiciousOperation("Session state and passed back state differ")

        try:
            token = get_token(self.request, auth_code)
        except InvalidClaimError:
            logger.error("Unable to validate token")
            raise SuspiciousOperation("Unable to validate token")

        self.request.session[TOKEN_SESSION_KEY] = dict(token)
        request.session.delete(f"{TOKEN_SESSION_KEY}_oath_state")
        request.session.delete(f"{TOKEN_SESSION_KEY}_oauth_nonce")

        # Get or create the user
        user = authenticate(request=request)

        if user:
            login(request, user)

        next_url = get_next_url(request) or getattr(settings, "LOGIN_REDIRECT_URL", "/")

        return redirect(next_url)
