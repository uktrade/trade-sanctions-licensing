import datetime

from apply_for_a_licence.choices import StatusChoices
from apply_for_a_licence.models import Licence
from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone
from utils.notifier import send_email


class Command(BaseCommand):
    help = (
        "Deletes licence applications older than DRAFT_APPLICATION_EXPIRY_DAYS number of days"
        "Sends an email to applications a week before DRAFT_APPLICATION_EXPIRY_DAYS"
        "Usage: pipenv run django_app/python manage.py delete_licence_applications"
    )

    def handle(self, *args, **options):
        delete_threshold = timezone.now() - datetime.timedelta(days=settings.DRAFT_APPLICATION_EXPIRY_DAYS + 1)
        # Delete applications older than DRAFT_APPLICATION_EXPIRY_DAYS
        stale_licences = Licence.objects.filter(created_at__lt=delete_threshold, status=StatusChoices.draft)
        for licence_object in stale_licences:
            licence_id = licence_object.id
            licence_object.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted Licence application {licence_id}"))

        # Email applicants whose licenses are 7 days from DRAFT_APPLICATION_EXPIRY_DAYS
        email_threshold = timezone.now() - datetime.timedelta(days=settings.DRAFT_APPLICATION_EXPIRY_DAYS - 7)
        email_licences = Licence.objects.filter(created_at__date=email_threshold.date(), status=StatusChoices.draft)

        for licence_object in email_licences:
            send_email(
                email=licence_object.applicant_user_email_address,
                template_id=settings.DELETE_LICENCE_APPLICATION_TEMPLATE_ID,
                context={
                    "application_number": licence_object.reference,
                    "application_url": reverse("dashboard"),
                },
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully sent email to {licence_object.applicant_user_email_address} "
                    f"for licence application {licence_object.id}"
                )
            )
