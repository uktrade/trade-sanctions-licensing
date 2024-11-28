import re

from django.conf import settings
from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestUpload(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Test upload works"""

    def test_upload(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.page.get_by_label("What is your purpose for").fill("Test purpose")
        self.page.get_by_role("button", name="Continue").click()
        self.page.wait_for_timeout(2000)  # Wait for the page to load
        self.page.get_by_label("Upload a file").set_input_files(settings.ROOT_DIR / "tests/test_frontend/fixtures/Test.pdf")
        expect(self.page.locator("text=Test.pdf")).to_be_visible()
        self.page.wait_for_timeout(2000)  # Wait for the doc to upload
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_test_id("supporting-documents")).to_have_text("Test.pdf")
