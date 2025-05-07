from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestTasklist(PlaywrightTestBase):
    """Tests for the start page"""

    def test_new_application_without_journey_returns_to_start(self):
        self.start_new_application()
        self.page.get_by_role("link", name="Your applications").click()
        self.page.get_by_role("link", name="Continue").first.click()
        expect(self.page.get_by_role("heading", name="Who do you want the licence")).to_be_visible()
