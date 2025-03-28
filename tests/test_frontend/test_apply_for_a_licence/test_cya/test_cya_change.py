import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    AboutTheServicesBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)
from tests.test_frontend.fixtures.data import LEGAL_GROUNDS_HEADERS


class TestCYAChange(StartBase, ProviderBase, RecipientBase, AboutTheServicesBase):
    """Test making changes on Check Your Answers."""

    def test_cya_changes(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.simple_about_the_service_task(self.page)
        self.recipient(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.check_your_answers(self.page)
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
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Name of recipient").fill("Test recipient change")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is the relationship").fill("Test relationship change")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.locator("text=Test recipient change")).to_be_visible()

    def test_cya_change_recipient_relationship(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.simple_about_the_service_task(self.page)
        self.recipient(self.page)
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
        self.check_your_answers(self.page, type="business")
        expect(self.page.get_by_test_id("recipient-relationship-1")).to_have_text("Test relationship")
        expect(self.page.get_by_test_id("recipient-relationship-2")).to_have_text("Friendship")

        # Change recipient 1
        self.page.get_by_role("link", name="Change Recipient 1 details").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is the relationship").fill("Enemies")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_test_id("recipient-relationship-1")).to_have_text("Enemies")
        expect(self.page.get_by_test_id("recipient-relationship-2")).to_have_text("Friendship")

    def test_cya_change_licensing_grounds_content(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.professional_and_business_service(self.page, pbs_services=["Legal advisory", "Accounting"])
        self.page.get_by_role("link", name="Your purpose for providing").click()
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_only"])
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/other-licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_excluded"])
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/services-purpose"))
        self.page.get_by_label("What is your purpose").fill("Test purpose")
        self.page.get_by_role("button", name="Continue").click()
        self.recipient(self.page)
        self.no_more_additions(self.page)
        self.check_your_answers(self.page, type="business", service="Professional and business services (Russia)")
        assert "licensinggroundsfortherelevantactivity" in self.page.get_by_test_id(
            "licensing_grounds_header"
        ).text_content().replace("\n", "").replace(" ", "")
        assert (
            "Licensing grounds for other services (not legal advisory)"
            in self.page.get_by_test_id("licensing_other_grounds_header").text_content()
        )

        # now changing
        self.page.get_by_test_id("change_professional_business_services_link").click()
        self.page.get_by_label("Accounting").uncheck()
        self.page.get_by_role("button", name="Continue").click()
        self.page.locator("textarea").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.locator("textarea").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        assert "licensinggroundsfortherelevantactivity" in self.page.get_by_test_id(
            "licensing_grounds_header"
        ).text_content().replace("\n", "").replace(" ", "")
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
        assert "licensinggroundsfortherelevantactivity" not in self.page.get_by_test_id(
            "licensing_grounds_header"
        ).text_content().replace("\n", "").replace(" ", "")
        assert "licensinggrounds" in self.page.get_by_test_id("licensing_grounds_header").text_content().replace(
            "\n", ""
        ).replace(" ", "")
        assert "Licensing grounds" in self.page.get_by_test_id("licensing_grounds_header").text_content()
        expect(self.page.get_by_test_id("licensing_other_grounds_header")).to_be_hidden()
