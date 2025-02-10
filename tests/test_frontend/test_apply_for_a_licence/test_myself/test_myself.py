import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestAddMyself(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Tests for the myself journey"""

    def test_located_in_uk(self):
        self.start_new_application()
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page, "myself")
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)
        """
        self.check_your_answers(self.page, type="myself")
        expect(self.page.get_by_test_id("who-the-licence-covers-name")).to_have_text("Test first name Test last name")
        expect(self.page.get_by_test_id("who-the-licence-covers-connection")).to_have_text("UK national located in the UK")
        expect(self.page.get_by_test_id("who-the-licence-covers-address")).to_have_text("A1, Town, AA0 0AA, United Kingdom")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)"""
        # todo - reinstate

    def test_add_another_individual_and_remove(self):
        self.start_new_application()
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        # expect(self.page.get_by_role("heading", name="You've added yourself plus 1 individual to the licence")).to_be_visible()
        # todo - reinstate
        self.page.get_by_role("button", name="Remove individual 1").click()
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        expect(self.page.get_by_role("heading", name="You've added yourself to the licence")).to_be_visible()
