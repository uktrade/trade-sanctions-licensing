from typing import Any

from authentication.config import OneLoginConfig
from authentication.constants import ONE_LOGIN_UNSET_NAME

from .base import *  # noqa

ENVIRONMENT = "local"

# DJANGO DEBUG TOOLBAR
INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

if env.profiling_enabled:
    # Line profiling allows you to see how long each line of code takes to execute
    # It can be useful for identifying bottlenecks in your code
    # enable profiling, load a page, and the result should appear in django_app/profiles
    PYINSTRUMENT_PROFILE_DIR = "profiles"
    MIDDLEWARE = MIDDLEWARE + [
        "pyinstrument.middleware.ProfilerMiddleware",
    ]

TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN = env.mock_sso_token

# we need to override AWS_ENDPOINT_URL environment variable to use localstack
os.environ["AWS_ENDPOINT_URL"] = f"http://localhost:{env.localstack_port}"

PROTOCOL = "http://"


class LocalOneLoginConfig(OneLoginConfig):
    CONFIGURATION_ENDPOINT = "http://localhost:28081/.well-known/openid-configuration"
    CACHE_KEY = "one_login_metadata_cache_local2"

    @staticmethod
    def get_user_create_mapping(profile: dict[str, Any]) -> dict[str, Any]:
        """Return a mapping of OneLogin profile data to user data."""
        return {
            "email": "test_user@example.com",
            "username": profile["sub"],
            "first_name": ONE_LOGIN_UNSET_NAME,
            "last_name": ONE_LOGIN_UNSET_NAME,
            "is_active": True,
        }


GOV_UK_ONE_LOGIN_CLIENT_ID = "my-client"
GOV_UK_ONE_LOGIN_CLIENT_SECRET = ""
GOV_UK_ONE_LOGIN_CONFIG = LocalOneLoginConfig
