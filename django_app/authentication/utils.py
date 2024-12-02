import base64
import logging
from typing import Any

from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from authlib.oidc.core import IDToken
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest, QueryDict
from django.urls import reverse

from . import types
from .constants import LOGIN_SCOPE
from .types import UserCreateData

logger = logging.getLogger(__name__)
TOKEN_SESSION_KEY = "_one_login_token"


def get_client_secret() -> bytes:
    """Returns the base64 decoded client secret"""
    return base64.b64decode(settings.GOV_UK_ONE_LOGIN_CLIENT_SECRET)


def get_client(request: HttpRequest) -> OAuth2Session:
    callback_url = reverse("authentication:callback")
    redirect_uri = request.build_absolute_uri(callback_url)

    session = OAuth2Session(
        client_id=settings.GOV_UK_ONE_LOGIN_CLIENT_ID,
        client_secret=get_client_secret(),
        token_endpoint_auth_method="private_key_jwt",
        redirect_uri=redirect_uri,
        scope=LOGIN_SCOPE,
        token=request.session.get(TOKEN_SESSION_KEY, None),
    )

    return session


def get_token(request: HttpRequest, auth_code: str) -> dict:
    client = get_client(request)
    config = settings.GOV_UK_ONE_LOGIN_CONFIG()

    client.register_client_auth_method(PrivateKeyJWT(token_endpoint=config.token_url))

    # https://docs.sign-in.service.gov.uk/integrate-with-integration-environment/authenticate-your-user/#receive-response-for-make-a-token-request
    token = client.fetch_token(
        url=config.token_url,
        code=auth_code,
        # If you’re requesting a refresh token, you must set this parameter to refresh_token.
        # Otherwise, you need to set the parameter to authorization_code.
        grant_type="authorization_code",
        # https://docs.sign-in.service.gov.uk/integrate-with-integration-environment/authenticate-your-user/#make-a-post-request-to-the-token-endpoint
        # Required value when using private_key_jwt auth.
        # client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    )

    validate_token(request, token)

    return token


def validate_token(request: HttpRequest, token: dict[str, Any]) -> None:
    config = settings.GOV_UK_ONE_LOGIN_CONFIG()
    stored_nonce = request.session.get(f"{TOKEN_SESSION_KEY}_oauth_nonce", None)

    # id_token contents:
    # https://docs.sign-in.service.gov.uk/integrate-with-integration-environment/authenticate-your-user/#understand-your-id-token
    claims = jwt.decode(
        token["id_token"],
        config.get_public_keys(),
        claims_cls=IDToken,
        claims_options={
            "iss": {"essential": True, "value": config.issuer},
            "aud": {"essential": True, "value": settings.GOV_UK_ONE_LOGIN_CLIENT_ID},
        },
        claims_params={"nonce": stored_nonce},
    )
    claims.validate()


def get_userinfo(client: OAuth2Session) -> types.UserInfo:
    config = settings.GOV_UK_ONE_LOGIN_CONFIG()
    resp = client.get(config.userinfo_url)
    resp.raise_for_status()

    return resp.json()


def get_one_login_logout_url(request: HttpRequest, post_logout_redirect_uri: str | None = None) -> str:
    """Get logout url for logging a user out of GOV.UK One Login.

    https://docs.sign-in.service.gov.uk/integrate-with-integration-environment/managing-your-users-sessions/#log-your-user-out-of-gov-uk-one-login

    :param request: Django HttpRequest instance
    :param post_logout_redirect_uri: Optional redirect url
    """

    url = settings.GOV_UK_ONE_LOGIN_CONFIG().end_session_url

    if post_logout_redirect_uri:
        qd = QueryDict(mutable=True)
        qd.update(
            {
                "id_token_hint": request.session[TOKEN_SESSION_KEY]["id_token"],
                "post_logout_redirect_uri": post_logout_redirect_uri,
            }
        )
        url = f"{url}?{qd.urlencode()}"

    return url


def get_or_create_user(id_value: str, user_data: UserCreateData) -> tuple[User, bool]:
    provider_email = user_data["email"]
    created = False

    try:
        # A legacy user is a user who has an email address as a username.
        user = User.objects.get(username=provider_email)
    except User.DoesNotExist:
        user, created = User.objects.get_or_create(username=id_value, defaults=user_data)

        if created:
            user.set_unusable_password()
            user.save()

    return user, created
