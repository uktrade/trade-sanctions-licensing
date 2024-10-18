from django.apps import AppConfig
from django.conf import settings


class ApplyForALicenceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apply_for_a_licence"

    def ready(self) -> None:
        if settings.ENVIRONMENT == "test":
            # if we're running on a test environment, we want to override the process_email_step method,
            # so we always use the same code for testing and don't send any emails
            from apply_for_a_licence.views.views_start import WhatIsYouEmailAddressView
            from config.settings.test import test_request_verify_code

            WhatIsYouEmailAddressView.form_valid = test_request_verify_code
