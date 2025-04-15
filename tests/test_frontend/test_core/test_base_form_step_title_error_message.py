import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestBaseFormStepTitleErrorMessage(PlaywrightTestBase):
    def test_error_in_title(self):
        self.page.get_by_test_id("start_new_application_link").click()
        self.page.get_by_test_id("start_new_application_link").click()
        self.page.get_by_role("button", name="Save and continue").click()

        expect(self.page).to_have_title(re.compile("Error: "))
