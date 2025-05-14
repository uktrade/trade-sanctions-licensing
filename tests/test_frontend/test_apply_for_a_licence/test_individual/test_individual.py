import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    AboutTheServicesBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestAddIndividual(StartBase, ProviderBase, AboutTheServicesBase, RecipientBase):
    """Tests for the individual journey"""

    def test_third_party_located_in_uk(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        self.page.get_by_role("link", name="Details of the individual you").click()
        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))
        self.no_more_additions(self.page)
        self.details_of_business_employing_individual(self.page)
        self.previous_licence(self.page)
        self.simple_about_the_service_task(self.page)
        self.recipient(self.page)
        self.no_more_additions(self.page)
        self.check_your_answers(self.page, type="individual")
        expect(self.page.get_by_test_id("who-the-licence-covers-name")).to_have_text("Test first name Test last name")
        expect(self.page.get_by_test_id("who-the-licence-covers-connection")).to_have_text("UK national located in the UK")
        expect(self.page.get_by_test_id("who-the-licence-covers-address")).to_have_text("A1, Town, AA0 0AA, United Kingdom")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)

    def test_add_another_individual_and_remove(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        self.page.get_by_role("link", name="Details of the individual you").click()
        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))
        expect(self.page.get_by_role("heading", name="You've added 2 individuals")).to_be_visible()
        self.page.get_by_role("button", name="Remove Individual 1").click()
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))
        expect(self.page.get_by_role("heading", name="You've added 1 individual")).to_be_visible()

    def test_uk_national_located_outside_the_uk(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        self.page.get_by_role("link", name="Details of the individual you").click()
        self.page.get_by_label("First name").fill("Test first name")
        self.page.get_by_label("Last name").fill("Test last name")
        self.page.get_by_label("UK national located outside the UK", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page, "individual")
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))

    def test_dual_national_located_in_uk(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        self.page.get_by_role("link", name="Details of the individual you").click()
        self.page.get_by_label("First name").fill("Test first name")
        self.page.get_by_label("Last name").fill("Test last name")
        self.page.get_by_label("Dual national (includes UK) located in the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(self.page, "individual")
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))

    def test_dual_national_located_outside_uk(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        self.page.get_by_role("link", name="Details of the individual you").click()
        self.page.get_by_label("First name").fill("Test first name")
        self.page.get_by_label("Last name").fill("Test last name")
        self.page.get_by_label("Dual national (includes UK) located outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page, "individual")
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))

    def test_non_uk_national(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        self.page.get_by_role("link", name="Details of the individual you").click()
        self.page.get_by_label("First name").fill("Test first name")
        self.page.get_by_label("Last name").fill("Test last name")
        self.page.get_by_label("Non-UK national located in the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(self.page, "individual")
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))

    def test_draft_individual_has_text(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        self.page.get_by_role("link", name="Details of the individual you").click()
        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Skip for now and return to").click()
        self.page.get_by_role("link", name="Details of the individual you").click()
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))
        expect(self.page.get_by_role("heading", name="You've added 2 individuals")).to_be_visible()
        expect(self.page.get_by_test_id("individual-address-2")).to_have_text("Not yet added")
        expect(self.page.get_by_test_id("individual-nationality-location-2")).to_have_text("Not yet added")
        expect(self.page.get_by_test_id("individual-name-2")).to_have_text("Not yet added")
