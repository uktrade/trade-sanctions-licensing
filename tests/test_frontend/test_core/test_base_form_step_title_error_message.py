import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestBaseFormStepTitleErrorMessage(PlaywrightTestBase):
    def test_error_text_in_title(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("button", name="Continue").click()

        expect(self.page).to_have_title(re.compile("Error: "))
