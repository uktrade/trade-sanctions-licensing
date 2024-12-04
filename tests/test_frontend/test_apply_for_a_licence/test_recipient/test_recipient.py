import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestRecipient(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Tests for different journeys during the recipient part of the journey"""

    def test_interception_or_monitoring_journey(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.page.get_by_label("No").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Interception or monitoring").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/sanctions-regime"))
        self.page.get_by_label("The Syria (Sanctions) (EU").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/describe-specific-activities"))

    def test_add_another_recipient_and_remove(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page, "recipient")
        self.page.get_by_label("What is the relationship").fill("Test relationship")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        expect(self.page.get_by_role("heading", name="You've added 2 recipients")).to_be_visible()
        self.page.get_by_role("button", name="Remove recipient 1").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        expect(self.page.get_by_role("heading", name="You've added 1 recipient")).to_be_visible()
