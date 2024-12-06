# mypy: ignore-errors

from config.settings.deploy.base import *  # noqa

DEBUG = False

ENVIRONMENT = "production"

# Django extra production sites
APPLY_FOR_A_LICENCE_EXTRA_DOMAIN = env.apply_for_a_licence_extra_domain
VIEW_A_LICENCE_EXTRA_DOMAIN = env.view_a_licence_extra_domain
