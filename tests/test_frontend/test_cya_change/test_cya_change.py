import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestCYAChange(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Test making a change on Check Your Answers."""

    def test_cya_changes(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)

        # Change your details
        self.page.get_by_role("link", name="Change your details").click()
        self.page.get_by_label("Full name").fill("Test name change")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.locator("text=Test name change")).to_be_visible()

        # Change business
        self.page.get_by_role("link", name="Change business 1 details").click()
        self.page.get_by_label("Name of business").fill("Test business change")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("No").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.locator("text=Test business change")).to_be_visible()

        # Change overview and purpose of the services
        self.page.get_by_role("link", name="Change the type of services").click()
        self.page.get_by_label("Mining, manufacturing or").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Describe the specific").fill("Test activities change")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your purpose for").fill("Test purposes change")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.locator("text=Mining, manufacturing or")).to_be_visible()
        expect(self.page.locator("text=Test activities change")).to_be_visible()
        expect(self.page.locator("text=Test purposes change")).to_be_visible()

        # Change recipient
        self.page.get_by_role("link", name="Change Recipient 1 details").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Name of recipient").fill("Test recipient change")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is the relationship").fill("Test relationship change")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.locator("text=Test recipient change")).to_be_visible()
