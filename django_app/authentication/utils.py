import base64
import json
import logging
from typing import Any

import requests
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from authlib.oidc.core import IDToken
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
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


class OneLoginConfig:
    CACHE_KEY = "one_login_metadata_cache"
    CACHE_EXPIRY = 60 * 60  # seconds

    def __init__(self) -> None:
        self._conf: dict[str, Any] = {}

    def get_public_keys(self) -> list[dict[str, str]]:
        # https://docs.sign-in.service.gov.uk/integrate-with-integration-environment/authenticate-your-user/#validate-your-id-token
        resp = requests.get(self.openid_config["jwks_uri"])
        resp.raise_for_status()
        data = resp.json()

        return data["keys"]

    @property
    def openid_config(self) -> dict[str, Any]:
        # Cached on instance
        if self._conf:
            logger.debug("one login conf: using instance attribute")
            return self._conf

        # Cached in redis store
        cache_config = cache.get(self.CACHE_KEY)
        if cache_config:
            logger.debug("one login conf: using cache value")
            self._conf = json.loads(cache_config)
            return self._conf

        # Retrieve and store value
        config = self._get_configuration()
        cache.set(self.CACHE_KEY, json.dumps(config), timeout=self.CACHE_EXPIRY)
        self._conf = config
        logger.debug("one login conf: using fresh value")

        return self._conf

    def _get_configuration(self) -> dict[str, Any]:
        resp = requests.get("https://oidc.integration.account.gov.uk/.well-known/openid-configuration")
        resp.raise_for_status()
        metadata = resp.json()

        return metadata

    @property
    def authorise_url(self) -> str:
        return self.openid_config["authorization_endpoint"]

    @property
    def token_url(self) -> str:
        return self.openid_config["token_endpoint"]

    @property
    def userinfo_url(self) -> str:
        return self.openid_config["userinfo_endpoint"]

    @property
    def end_session_url(self) -> str:
        return self.openid_config["end_session_endpoint"]

    @property
    def issuer(self) -> str:
        return self.openid_config["issuer"]


def get_token(request: HttpRequest, auth_code: str) -> dict:
    client = get_client(request)
    config = OneLoginConfig()

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
        client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    )

    validate_token(request, token)

    return token


def validate_token(request: HttpRequest, token: dict[str, Any]) -> None:
    config = OneLoginConfig()
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
    config = OneLoginConfig()
    resp = client.get(config.userinfo_url)
    resp.raise_for_status()

    return resp.json()


def get_one_login_logout_url(request: HttpRequest, post_logout_redirect_uri: str | None = None) -> str:
    """Get logout url for logging a user out of GOV.UK One Login.

    https://docs.sign-in.service.gov.uk/integrate-with-integration-environment/managing-your-users-sessions/#log-your-user-out-of-gov-uk-one-login

    :param request: Django HttpRequest instance
    :param post_logout_redirect_uri: Optional redirect url
    """

    url = OneLoginConfig().end_session_url

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
