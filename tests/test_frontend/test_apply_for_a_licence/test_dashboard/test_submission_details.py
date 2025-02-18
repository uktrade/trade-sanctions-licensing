from datetime import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import expect

from tests.factories import LicenceFactory
from tests.test_frontend.conftest import PlaywrightTestBase


class TestApplicationDetails(PlaywrightTestBase):
    def test_submitted_on(self):
        user = User.objects.get(email="apply_test_user@example.com")
        submitted_licence = LicenceFactory(
            user=user,
            status="submitted",
            submitted_at=datetime(2025, 2, 14, tzinfo=timezone.get_current_timezone()),
            reference="111111",
        )

        self.go_to_path(reverse("dashboard"))
        expect(self.page.get_by_text(f"Submitted on {submitted_licence.submitted_at.strftime('%d %B %Y')}")).to_be_visible()
        expect(self.page.get_by_text(f"Your reference: {submitted_licence.reference}")).to_be_visible()
