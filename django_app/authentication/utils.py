import base64
import logging
from typing import Any

from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from authlib.oidc.core import IDToken
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse

from . import types
from .constants import LOGIN_SCOPE

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
