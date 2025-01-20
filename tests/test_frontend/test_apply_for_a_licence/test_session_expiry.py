from time import sleep

from django.test import override_settings
from django.urls import reverse
from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestSessionExpiry(PlaywrightTestBase):
    """Tests that session expiry dialog appears"""

    @override_settings(SESSION_COOKIE_AGE=4 * 60)
    def test_dialog_appears(self):
        self.go_to_path(reverse("submitter_reference"))
        expect(self.page.get_by_test_id("session_expiry_time_remaining")).to_be_visible()
        assert self.page.get_by_test_id("session_expiry_time_remaining").text_content() == "4 minutes"

    @override_settings(SESSION_COOKIE_AGE=303)
    def test_clicking_ping_session_button_resets_timer(self):
        self.go_to_path(reverse("submitter_reference"))
        sleep(4)
        self.page.get_by_test_id("ping_session_button").click()
        expect(self.page.get_by_test_id("session_expiry_time_remaining")).to_be_hidden()

        # now checking that it appears again after a while.
        sleep(4)
        expect(self.page.get_by_test_id("session_expiry_time_remaining")).to_be_visible()

    @override_settings(SESSION_COOKIE_AGE=60)
    def test_second_countdown(self):
        self.go_to_path(reverse("submitter_reference"))
        expect(self.page.get_by_test_id("session_expiry_time_remaining")).to_be_visible()
        assert self.page.get_by_test_id("session_expiry_time_remaining").text_content() == "60 seconds"
        sleep(1)
        assert self.page.get_by_test_id("session_expiry_time_remaining").text_content() == "59 seconds"

    @override_settings(SESSION_COOKIE_AGE=60)
    def test_non_javascript_version(self):
        non_js_page = self.browser.new_context(java_script_enabled=False).new_page()
        self.go_to_path(reverse("submitter_reference"), page=non_js_page)
        expect(non_js_page.get_by_test_id("non_js_session_expiry_banner")).to_be_visible()
        expect(non_js_page.get_by_text("Your application will be deleted if you're inactive for 1 minute")).to_be_visible()

        # now testing this does not appear on normal
        self.go_to_path(reverse("submitter_reference"))
        expect(self.page.get_by_test_id("non_js_session_expiry_banner")).to_be_hidden()
        expect(self.page.get_by_text("Your application will be deleted if you're inactive for 1 minute")).to_be_hidden()

    @override_settings(SESSION_COOKIE_AGE=1)
    def test_redirect_on_session_expire(self):
        self.go_to_path(reverse("submitter_reference"))
        expect(self.page.get_by_test_id("session_expiry_time_remaining")).to_be_visible()
        # might as well test the grammar rule
        assert self.page.get_by_test_id("session_expiry_time_remaining").text_content() == "1 second"
        sleep(1)
        expect(self.page.get_by_role("heading", name="Your application has been")).to_be_visible()
