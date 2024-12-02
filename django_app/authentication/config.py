import json
import logging
from typing import Any

import requests
from authentication.constants import ONE_LOGIN_UNSET_NAME
from authentication.types import UserInfo
from django.core.cache import cache

logger = logging.getLogger(__name__)


class OneLoginConfig:
    CACHE_KEY = "one_login_metadata_cache"
    CACHE_EXPIRY = 60 * 60  # seconds
    CONFIGURATION_ENDPOINT = "https://oidc.integration.account.gov.uk/.well-known/openid-configuration"

    def __init__(self) -> None:
        self._conf: dict[str, Any] = {}

    @staticmethod
    def get_user_create_mapping(profile: UserInfo) -> dict[str, Any]:
        """Return a mapping of OneLogin profile data to user data."""
        return {
            "email": profile["email"],
            "username": profile["sub"],
            "first_name": ONE_LOGIN_UNSET_NAME,
            "last_name": ONE_LOGIN_UNSET_NAME,
            "is_active": True,
        }

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
        resp = requests.get(self.CONFIGURATION_ENDPOINT)
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
