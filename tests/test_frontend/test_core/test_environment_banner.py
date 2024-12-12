from django.test import override_settings
from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestEnvironmentBanner(PlaywrightTestBase):
    """Tests the non-production banner appears"""

    @override_settings(ENVIRONMENT="production", DEBUG=False)
    def test_banner_does_not_appear(self):
        self.page.goto(self.base_url)
        expect(self.page.get_by_test_id("environment_banner")).to_be_hidden()

    @override_settings(ENVIRONMENT="local", DEBUG=True)
    def test_banner_appears(self):
        self.page.goto(self.base_url)
        expect(self.page.get_by_test_id("environment_banner")).to_be_visible()
        expect(self.page.get_by_text("Environment: local")).to_be_visible()
