import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestCYAChange(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Test making changes on Check Your Answers."""

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
        self.page.get_by_test_id("change_your_details_link").click()
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

    def test_cya_change_recipient_relationship(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        # Add another recipient
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page, "recipient")
        self.page.get_by_label("What is the relationship").fill("Friendship")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        expect(self.page.get_by_role("heading", name="You've added 2 recipients")).to_be_visible()
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)
        expect(self.page.get_by_test_id("recipient-relationship-1")).to_have_text("Test relationship")
        expect(self.page.get_by_test_id("recipient-relationship-2")).to_have_text("Friendship")

        # Change recipient 1
        self.page.get_by_role("link", name="Change Recipient 1 details").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is the relationship").fill("Enemies")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_test_id("recipient-relationship-1")).to_have_text("Enemies")
        expect(self.page.get_by_test_id("recipient-relationship-2")).to_have_text("Friendship")

    def test_cya_change_licensing_grounds_content(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        self.no_more_additions(self.page)
        self.recipient_legal_and_other(self.page)
        self.no_more_additions(self.page)
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your purpose").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("button", name="Continue").click()
        assert (
            "Licensing grounds for the relevant activity" in self.page.get_by_test_id("licensing_grounds_header").text_content()
        )
        assert (
            "Licensing grounds for other services (not legal advisory)"
            in self.page.get_by_test_id("licensing_other_grounds_header").text_content()
        )

        # now changing
        self.page.get_by_test_id("change_professional_business_services_link").click()
        self.page.get_by_label("Auditing").uncheck()
        self.page.get_by_role("button", name="Continue").click()
        self.page.locator("textarea").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.locator("textarea").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        assert (
            "Licensing grounds for the relevant activity" in self.page.get_by_test_id("licensing_grounds_header").text_content()
        )
        expect(self.page.get_by_test_id("licensing_other_grounds_header")).to_be_hidden()

        # now changing again
        self.page.get_by_test_id("change_professional_business_services_link").click()
        self.page.get_by_label("Auditing").check()
        self.page.get_by_label("Legal advisory").uncheck()
        self.page.get_by_role("button", name="Continue").click()
        self.page.locator("textarea").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.locator("textarea").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        assert (
            "Licensing grounds for the relevant activity"
            not in self.page.get_by_test_id("licensing_grounds_header").text_content()
        )
        assert "Licensing grounds" in self.page.get_by_test_id("licensing_grounds_header").text_content()
        expect(self.page.get_by_test_id("licensing_other_grounds_header")).to_be_hidden()
