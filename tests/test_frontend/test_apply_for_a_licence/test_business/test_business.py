import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestAddBusiness(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Tests for the business journey."""

    def test_third_party_located_in_uk(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)
        self.check_your_answers(self.page)
        expect(self.page.get_by_test_id("who-the-licence-covers-name")).to_have_text("business")
        expect(self.page.get_by_test_id("who-the-licence-covers-address")).to_have_text("A1, Town, AA0 0AA, United Kingdom")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        self.check_submission_complete_page(self.page)

    def test_not_third_party_located_outside_uk(self):
        self.start_new_application()
        self.business_not_third_party(self.page)
        self.provider_business_located_outside_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)
        self.check_your_answers(self.page, third_party=False)
        expect(self.page.get_by_test_id("who-the-licence-covers-name")).to_have_text("business")
        expect(self.page.get_by_test_id("who-the-licence-covers-address")).to_have_text("A1, Town, Germany")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)

    def test_add_another_business_and_remove(self):
        self.start_new_application()
        self.business_not_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        expect(self.page.get_by_role("heading", name="You've added 2 businesses")).to_be_visible()
        self.page.get_by_role("button", name="Remove business 1").click()
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        expect(self.page.get_by_role("heading", name="You've added 1 business")).to_be_visible()

    def test_back_button_doesnt_duplicate(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)

        expect(self.page.get_by_role("heading", name="You've added 1 business")).to_be_visible()

        self.page.go_back()
        self.page.go_back()
        self.page.go_back()

        # now let's go forward again
        self.page.go_forward()
        self.page.go_forward()
        self.page.go_forward()

        # we still should see only 1 business, no duplicate created
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        expect(self.page.get_by_role("heading", name="You've added 1 business")).to_be_visible()
