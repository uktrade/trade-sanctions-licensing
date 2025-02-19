import datetime
from unittest.mock import patch

import pytest
from apply_for_a_licence.choices import StatusChoices
from apply_for_a_licence.models import Licence
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse

from tests.factories import LicenceFactory


@pytest.mark.django_db
class TestDeletesStaleApplications:
    def test_only_deletes_draft_applications(self):
        past_date = datetime.datetime(2020, 5, 17)

        licence_1 = LicenceFactory(id=1, reference="123", status=StatusChoices.draft)
        licence_1.created_at = past_date
        licence_1.save()
        licence_2 = LicenceFactory(id=2, reference="456", status=StatusChoices.submitted)
        licence_2.created_at = past_date
        licence_2.save()
        assert Licence.objects.count() == 2

        call_command("manage_applications")
        licences = Licence.objects.all()
        assert Licence.objects.count() == 1
        assert licence_1 not in licences
        assert licence_2 in licences

    @override_settings(DRAFT_APPLICATION_EXPIRY_DAYS=3)
    def test_only_deletes_applications_after_expiry(self):
        expired_date = datetime.datetime.now() - datetime.timedelta(days=4)
        non_expired_date = datetime.datetime.now() - datetime.timedelta(days=3)

        licence_1 = LicenceFactory(id=1, reference="123", status=StatusChoices.draft)
        licence_1.created_at = expired_date
        licence_1.save()
        licence_2 = LicenceFactory(id=2, reference="456", status=StatusChoices.draft)
        licence_2.created_at = non_expired_date
        licence_2.save()
        assert Licence.objects.count() == 2

        call_command("manage_applications")
        licences = Licence.objects.all()
        assert Licence.objects.count() == 1
        assert licence_1 not in licences
        assert licence_2 in licences


@pytest.mark.django_db
class TestSendsEmail:
    @override_settings(DRAFT_APPLICATION_EXPIRY_DAYS=8)
    @patch("core.management.commands.manage_applications.send_email")
    def test_sends_email_one_week_before(self, mock_email):
        email_date = datetime.datetime.now() - datetime.timedelta(days=1)
        non_email_date = datetime.datetime.now() - datetime.timedelta(days=2)

        licence_1 = LicenceFactory(id=1, reference="123", status=StatusChoices.draft)
        licence_1.created_at = email_date
        licence_1.save()
        licence_2 = LicenceFactory(id=2, reference="456", status=StatusChoices.draft)
        licence_2.created_at = non_email_date
        licence_2.save()
        licence_3 = LicenceFactory(id=3, reference="789", status=StatusChoices.draft)
        licence_3.created_at = datetime.datetime.now()
        licence_3.save()
        assert Licence.objects.count() == 3

        call_command("manage_applications")
        assert Licence.objects.count() == 3
        args, kwargs = mock_email.call_args
        mock_email.assert_called_once()
        assert kwargs["email"] == licence_1.applicant_user_email_address
        assert kwargs["context"]["application_number"] == licence_1.reference
        assert kwargs["context"]["application_url"] == reverse("dashboard")

    @override_settings(DRAFT_APPLICATION_EXPIRY_DAYS=8)
    @patch("core.management.commands.manage_applications.send_email")
    def test_only_sends_email_to_draft_licence(self, mock_email):
        email_date = datetime.datetime.now() - datetime.timedelta(days=1)

        licence_1 = LicenceFactory(id=1, reference="123", status=StatusChoices.draft)
        licence_1.created_at = email_date
        licence_1.save()
        licence_2 = LicenceFactory(id=2, reference="456", status=StatusChoices.submitted)
        licence_2.created_at = email_date
        licence_2.save()
        assert Licence.objects.count() == 2

        call_command("manage_applications")
        assert Licence.objects.count() == 2
        args, kwargs = mock_email.call_args
        mock_email.assert_called_once()
        assert kwargs["email"] == licence_1.applicant_user_email_address
        assert kwargs["context"]["application_number"] == licence_1.reference
        assert kwargs["context"]["application_url"] == reverse("dashboard")
