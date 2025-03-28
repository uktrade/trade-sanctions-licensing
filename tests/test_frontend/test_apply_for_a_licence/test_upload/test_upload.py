import re

import pytest
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

    def get_to_upload_page(self):
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

    def test_upload(self):
        self.get_to_upload_page()
        self.page.get_by_label("Upload a file").set_input_files(settings.ROOT_DIR / "tests/test_frontend/fixtures/Test.pdf")
        expect(self.page.locator("text=Test.pdf")).to_be_visible()
        self.page.wait_for_timeout(2000)  # Wait for the doc to upload
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_test_id("supporting-documents")).to_have_text("Test.pdf")

    @pytest.mark.usefixtures("patched_clean_document")
    def test_malware_file_raises_error(self):
        self.get_to_upload_page()
        self.page.get_by_label("Upload a file").set_input_files(
            settings.ROOT_DIR / "tests/test_frontend/fixtures/mock_malware_file.txt"
        )
        self.page.wait_for_timeout(2000)  # Wait for the doc to upload
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_text("The selected file contains a virus")).to_be_visible()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("mock_malware_file.txt")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/upload-documents"))
        self.page.get_by_text("Reset session").click()

    def test_incorrect_file_type(self):
        self.get_to_upload_page()
        self.page.get_by_label("Upload a file").set_input_files(
            settings.ROOT_DIR / "tests/test_frontend/fixtures/incorrect_file_type.sh"
        )
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        assert "incorrect_file_type.sh cannot be uploaded" in self.page.locator(".govuk-error-summary__body").text_content()
        # checking that the file row is not visible
        expect(self.page.locator(".moj-multi-file__uploaded-files")).not_to_be_visible()
        # you should still be able to continue
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
