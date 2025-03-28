from typing import Any

import sentry_sdk
from django.conf import settings
from django.http import HttpResponse
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient


def send_email(email: str, context: dict[str, Any], template_id: str, reference: str | None = None) -> HttpResponse | bool:
    """Send an email using the GOV.UK Notify API."""
    client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
    try:
        send_report = client.send_email_notification(
            email_address=email,
            template_id=template_id,
            personalisation=get_context(context),
            reference=reference,
        )
        return send_report
    except HTTPError as err:
        # something has gone wrong, let's fail silently and report the error
        sentry_sdk.capture_exception(err)
        return False


def get_context(extra_context: dict | None = None) -> dict[str, Any]:
    extra_context = extra_context or {}
    footer = "Apply for a Licence service"
    context = {
        "footer": footer,
    }
    context.update(extra_context)
    return context
