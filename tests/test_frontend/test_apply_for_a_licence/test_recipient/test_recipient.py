import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    AboutTheServicesBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestRecipient(StartBase, ProviderBase, RecipientBase, AboutTheServicesBase):
    """Tests for different journeys during the recipient part of the journey"""

    def test_interception_or_monitoring_journey(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.interception_or_monitoring_service(self.page)
        expect(self.page).to_have_url(re.compile(r".*/describe-specific-activities"))

    def test_add_another_recipient_and_remove(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.recipient(self.page)
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
        self.page.get_by_role("button", name="Remove Recipient 1").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        expect(self.page.get_by_role("heading", name="You've added 1 recipient")).to_be_visible()

    def test_changing_recipient_same_location(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.recipient(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.page.get_by_text("Change").click()
        self.page.get_by_text("In the UK").click()
        self.page.get_by_role("button", name="Continue").click()
        assert self.page.locator("input[name='name']").input_value() == "business"  # checking pre-fill
        self.page.get_by_role("button", name="Continue").click()
        assert self.page.locator("[name='relationship_provider']").input_value() == "Test relationship"  # checking pre-fill
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        expect(self.page.get_by_role("heading", name="You've added 1 recipient")).to_be_visible()

    def test_changing_recipient_different_location(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.recipient(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.page.get_by_text("Change").click()
        self.page.get_by_text("Outside the UK").click()
        self.page.get_by_role("button", name="Continue").click()
        assert self.page.locator("input[name='address_line_1']").input_value() == ""  # should be wiped

    def test_draft_recipient_has_text(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.recipient(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Skip for now and return to").click()
        self.page.get_by_role("link", name="Recipient contact details").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        expect(self.page.get_by_role("heading", name="You've added 2 recipients")).to_be_visible()
        expect(self.page.get_by_test_id("recipient-address-2")).to_have_text("Not yet added")
        expect(self.page.get_by_test_id("recipient-name-2")).to_have_text("Not yet added")
