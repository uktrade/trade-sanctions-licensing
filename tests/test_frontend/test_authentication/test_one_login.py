from tests.test_frontend.conftest import PlaywrightTestBase


class TestLoginRequired(PlaywrightTestBase):
    """Tests for the business journey."""

    def test_login_required_flow(self):
        self.page.goto(self.base_url)
        self.page.get_by_placeholder("Enter any login").click()
        self.page.get_by_placeholder("Enter any login").fill("test")
        self.page.get_by_placeholder("and password").click()
        self.page.get_by_placeholder("and password").fill("test")
        self.page.get_by_role("button", name="Sign-in").click()
        ...
