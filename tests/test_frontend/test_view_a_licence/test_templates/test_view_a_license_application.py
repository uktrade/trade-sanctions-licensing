from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import expect

from tests.factories import LicenceFactory, UserFactory
from tests.test_frontend.test_view_a_licence.conftest import PlaywrightTestBase


class TestApplicationDetails(PlaywrightTestBase):
    def test_submitted_on_detail(self):

        submitting_user = UserFactory(email="submitting_user@example.com", username="submitting_user", is_active=True)

        submitted_licence = LicenceFactory.create(
            user=submitting_user,
            status="submitted",
            submitted_at=datetime(2025, 2, 14, tzinfo=timezone.get_current_timezone()),
        )
        submitted_licence.assign_reference()
        submitted_licence.save()

        self.page.goto(
            self.base_url + reverse("view_a_licence:view_application", kwargs={"reference": submitted_licence.reference})
        )

        expect(self.page.get_by_text(f"Submitted on: {submitted_licence.submitted_at.strftime('%d %B %Y')}")).to_be_visible()


class TestApplicationList(PlaywrightTestBase):
    def test_list_has_four_pages_when_paginated_by_10(self):

        submitting_user = UserFactory(email="submitting_user@example.com", username="submitting_user", is_active=True)

        for i in range(31):
            submitted_licence = LicenceFactory.create(
                user=submitting_user,
                status="submitted",
                submitted_at=datetime(2025, 2, 14, tzinfo=timezone.get_current_timezone()),
            )
            submitted_licence.assign_reference()
            submitted_licence.save()

        self.page.goto(self.base_url + reverse("view_a_licence:application_list"))

        pagination = self.page.locator(".govuk-pagination")
        expect(pagination).to_be_visible()

        # Check that there are 4 pages for the list of 31 items
        pagination_items = self.page.locator(".govuk-pagination__item")
        expect(pagination_items).to_have_count(4)

        # Check that the current page shows the correct number
        current_page = self.page.locator(".govuk-pagination__item--current")
        expect(current_page).to_have_text("1")

        # Check that each page only shows 10 licenses
        license_items = self.page.locator("h3.govuk-heading-s:has-text('View licence application reference:')")
        expect(license_items).to_have_count(10)

        # Check that page 4 has 1 item
        license_items = self.page.locator("h3.govuk-heading-s:has-text('View licence application reference:')")
        expect(license_items).to_have_count(1)
