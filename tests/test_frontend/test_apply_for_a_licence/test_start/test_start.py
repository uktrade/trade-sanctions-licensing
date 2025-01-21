import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestStart(PlaywrightTestBase):
    """Tests for the start page"""

    def test_no_input_raises_error(self):
        self.start_new_application()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role("link", name="Select who you want the").click()

    def test_uk_nexus_helptext_present(self):
        self.start_new_application()
        self.page.get_by_text("What do we mean by UK nexus?").click()
        self.page.get_by_text("You must comply with UK").click()
        self.page.get_by_label("Named individuals with a UK").check()

    def test_business_input_goes_to_third_party(self):
        self.start_new_application()
        self.page.get_by_role("heading", name="Who do you want the licence").click()
        self.page.get_by_label("A business or businesses with").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Are you a third-party").click()
        expect(self.page).to_have_url(re.compile(r".*/third-party"))

    def test_individual_input_goes_to_third_party(self):
        self.start_new_application()
        self.page.get_by_role("heading", name="Who do you want the licence").click()
        self.page.get_by_label("Named individuals with a UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Are you a third-party").click()
        expect(self.page).to_have_url(re.compile(r".*/third-party"))

    def test_myself_input_goes_to_myself_details(self):
        self.start_new_application()
        self.page.get_by_role("heading", name="Who do you want the licence").click()
        self.page.get_by_label("Myself").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_text("Your details", exact=True).click()
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
