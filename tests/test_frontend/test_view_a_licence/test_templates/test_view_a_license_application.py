from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import expect

from tests.factories import LicenceFactory, UserFactory
from tests.test_frontend.conftest import PlaywrightTestBase


class TestApplicationDetails(PlaywrightTestBase):
    def test_submitted_on_detail(self):

        # viewing_user = UserFactory(
        #     email="apply_test_user@example.com",
        #     username="apply_test_user",
        #     is_staff=True,
        #     is_active=True
        # )

        submitting_user = UserFactory(email="submitting_user@example.com", username="submitting_user", is_active=True)

        submitted_time = timezone.now()
        submitted_licence = LicenceFactory.create(user=submitting_user, status="submitted", submitted_at=submitted_time)
        submitted_licence.assign_reference()
        submitted_licence.save()

        self.page.goto(
            self.base_url + reverse("view_a_licence:view_application", kwargs={"reference": submitted_licence.reference})
        )

        expect(self.page.get_by_text(f"Submitted on:{submitted_licence.submitted_at.strftime('%d %B %Y')}")).to_be_visible()
