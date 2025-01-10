# mypy: ignore-errors
from .base import *  # noqa

ENVIRONMENT = "local"

# DJANGO DEBUG TOOLBAR
INSTALLED_APPS += ["debug_toolbar"]

#  type: ignore[used-before-def]
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

CURRENT_BRANCH = env.git_current_branch
CURRENT_COMMIT = env.git_current_commit
