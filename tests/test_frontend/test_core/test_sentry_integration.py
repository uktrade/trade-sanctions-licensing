from django.test import override_settings
from playwright._impl._errors import Error

from tests.test_frontend.conftest import PlaywrightTestBase


class TestSessionExpiry(PlaywrightTestBase):
    """Tests that session expiry dialog appears"""

    @override_settings(
        SENTRY_ENABLED=True,
        SENTRY_DSN="https://example.com",
        SENTRY_ENVIRONMENT="test",
        SENTRY_ENABLE_TRACING=False,
        SENTRY_TRACES_SAMPLE_RATE=1.0,
    )
    def test_script_is_working(self):
        self.page.goto(self.base_url)
        assert self.page.evaluate("Sentry.isInitialized") is True
        assert self.page.evaluate("Sentry.getClient")["ct"]["dsn"] == "https://example.com"
        assert self.page.evaluate("Sentry.getClient")["ct"]["environment"] == "test"

    @override_settings(
        SENTRY_ENABLED=False,
    )
    def test_sentry_disabled_script_no_show(self):
        self.page.goto(self.base_url)
        with self.assertRaises(Error):
            self.page.evaluate("Sentry.isInitialized")
