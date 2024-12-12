import os
import re
from unittest import mock
from unittest.mock import MagicMock

import notifications_python_client
import pytest
from apply_for_a_licence.forms.forms_documents import UploadDocumentsForm
from core.sites import SiteName
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import override_settings
from django.test.testcases import LiveServerTestCase
from django_chunk_upload_handlers.clam_av import VirusFoundInFileException
from playwright.sync_api import expect, sync_playwright
from utils import notifier

from tests.test_frontend.fixtures import data


@override_settings(DEBUG=True)
class PlaywrightTestBase(LiveServerTestCase):
    """Base class for Playwright tests. Sets up the Playwright browser, page per test, and deals with the Site objects."""

    @classmethod
    def setUpClass(cls) -> None:
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()

        # starting playwright stuff
        cls.playwright = sync_playwright().start()

        # playwright on CirlceCI exhibits some tricky behaviour whereby the HEADLESS argument is passed as a string
        # instead of a bool. CircleCI should always be headless anyway
        if "CIRCLECI" in os.environ:
            cls.browser = cls.playwright.firefox.launch(headless=True)
        else:
            cls.browser = cls.playwright.firefox.launch(headless=settings.HEADLESS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

        super().tearDownClass()

    def setUp(self) -> None:
        #  Create a new page for each test
        if settings.SAVE_VIDEOS:
            self.page = self.browser.new_page(record_video_dir="video-test-results/")
        else:
            self.page = self.browser.new_page()

        # need to re-create the Site objects to match the new port of the live server,
        # first we just need to get the original port
        first_site = Site.objects.first()
        self.original_port = first_site.domain.split(":")[-1]

        # deleting
        Site.objects.all().delete()

        # recreating with the new port
        Site.objects.create(
            name=SiteName.apply_for_a_licence,
            domain=f"{SiteName.apply_for_a_licence}:{self.server_thread.port}",
        )
        Site.objects.create(
            name=SiteName.view_a_licence,
            domain=f"{SiteName.view_a_licence}:{self.server_thread.port}",
        )

    def tearDown(self) -> None:
        if settings.SAVE_VIDEOS:
            # Rename the video in the test results directory, so it's readable
            # 1231239190wei9cwice023r239230.webm -> video-test-results/ClassName-test_method.webm
            old_name = self.page.video.path()
            os.replace(old_name, settings.ROOT_DIR / f"video-test-results/{type(self).__name__}-{self._testMethodName}.webm")

        # resetting the Site objects to their original state
        Site.objects.all().delete()
        Site.objects.create(
            name=SiteName.apply_for_a_licence,
            domain=f"{SiteName.apply_for_a_licence}:{self.original_port}",
        )
        Site.objects.create(
            name=SiteName.view_a_licence,
            domain=f"{SiteName.view_a_licence}:{self.original_port}",
        )

        # close the page
        self.page.close()

    @property
    def base_host(self) -> str:
        return settings.APPLY_FOR_A_LICENCE_DOMAIN.split(":")[0]

    @property
    def base_url(self) -> str:
        return f"http://{self.base_host}:{self.server_thread.port}"

    def verify_email_details(self, page):
        self.email_details(page)
        self.verify_email(page)

    def check_your_answers(self, page, third_party=True, type="business"):
        expect(page).to_have_url(re.compile(r".*/check-your-answers"))
        if type != "myself":
            self.cya_your_details(page, third_party)
        expect(page.get_by_test_id("previous-licence")).to_have_text("No")
        self.cya_overview(page)
        self.cya_recipients(page)
        self.cya_purposes(page)

    @staticmethod
    def email_details(page, details=data.EMAIL_DETAILS):
        page.get_by_label("What is your email address?").fill(details["email"])
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def verify_email(page, details=data.EMAIL_DETAILS):
        page.get_by_role("heading", name="We've sent you an email").click()
        page.get_by_label("Enter the 6 digit security").fill(details["verify_code"])
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def fill_uk_address_details(page, type="business", details=data.UK_ADDRESS_DETAILS):
        if type == "recipient" or type == "business":
            page.get_by_label(f"Name of {type}").fill(details["name"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("Postcode").fill(details["postcode"])
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def fill_non_uk_address_details(page, type="business", details=data.NON_UK_ADDRESS_DETAILS):
        if type == "recipient" or type == "business":
            page.get_by_label(f"Name of {type}").fill(details["name"])
        page.get_by_label("Country").select_option(details["country"])
        page.get_by_label("Town").fill(details["town"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def declaration_and_complete_page(page):
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Submit").click()

    @staticmethod
    def no_more_additions(page):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def your_details(page, type="business", details=data.YOUR_DETAILS):
        if type == "myself":
            page.get_by_label("First name").fill("Test first name")
            page.get_by_label("Last name").fill("Test last name")
            page.get_by_label("UK national located in the UK", exact=True).check()
            page.get_by_role("button", name="Continue").click()
        else:
            page.get_by_label("Full name").fill(details["full_name"])
            page.get_by_label("Business you work for").fill(details["business"])
            page.get_by_label("Your role").fill(details["role"])
            page.get_by_role("button", name="Continue").click()

    @staticmethod
    def cya_your_details(page, third_party):
        expect(page.get_by_test_id("your-details-name")).to_have_text("Test full name")
        expect(page.get_by_test_id("your-details-business")).to_have_text("Test business")
        expect(page.get_by_test_id("your-details-role")).to_have_text("Test role")
        if third_party:
            expect(page.get_by_test_id("your-details-third-party")).to_have_text("Yes")
        else:
            expect(page.get_by_test_id("your-details-third-party")).to_have_text("No")

    @staticmethod
    def cya_overview(page):
        expect(page.get_by_test_id("services-type")).to_have_text("Energy-related services (Russia)")
        expect(page.get_by_test_id("services-description")).to_have_text("Test description")

    @staticmethod
    def cya_recipients(page):
        expect(page.get_by_test_id("recipient-name-and-address-1")).to_have_text("business\nA1, Town, AA0 0AA, United Kingdom")
        expect(page.get_by_test_id("recipient-relationship-1")).to_have_text("Test relationship")

    @staticmethod
    def cya_purposes(page):
        expect(page.get_by_test_id("purpose")).to_have_text("Test purpose")
        expect(page.get_by_test_id("supporting-documents")).to_have_text("None uploaded")

    @staticmethod
    def check_submission_complete_page(page):
        expect(page).to_have_url(re.compile(r".*/application-complete"))
        expect(page.locator("text=Submission complete")).to_be_visible()
        expect(page.locator("text=Your reference number")).to_be_visible()


class StartBase(PlaywrightTestBase):
    def business_third_party(self, page):
        page.get_by_label("A business or businesses with").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)

    def business_not_third_party(self, page):
        page.get_by_label("A business or businesses with").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)

    def individual_third_party(self, page):
        page.get_by_label("Named individuals with a UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)

    def myself(self, page):
        page.get_by_label("Myself").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)


class ProviderBase(PlaywrightTestBase):
    def provider_business_located_in_uk(self, page):
        self.your_details(page, "business")
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "business")

    def provider_business_located_outside_uk(self, page):
        self.your_details(page, "business")
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(page)

    def provider_individual_located_in_uk(self, page, first_individual_added=False):
        if first_individual_added:
            self.your_details(page, "individual")
        page.get_by_label("First name").fill("Test first name")
        page.get_by_label("Last name").fill("Test last name")
        page.get_by_label("UK national located in the UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "individual")

    def provider_myself_located_in_uk(self, page):
        self.your_details(page, "myself")
        self.fill_uk_address_details(page, "individual")


class RecipientBase(PlaywrightTestBase):
    def recipient(self, page, service_type):
        page.get_by_label(service_type).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Describe the specific").fill("Test description")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "recipient")
        page.get_by_label("What is the relationship").fill("Test relationship")
        page.get_by_role("button", name="Continue").click()

    def recipient_simple(self, page, reporter_type="business"):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        self.recipient(page, "Energy-related services (")

    def recipient_legal(self, page, reporter_type="business"):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        page.get_by_label("Professional and business").check()
        page.get_by_role("button", name="Continue").click()
        self.recipient(page, "Legal advisory")

    def recipient_non_legal(self, page, reporter_type="business"):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        page.get_by_label("Professional and business").check()
        page.get_by_role("button", name="Continue").click()
        self.recipient(page, "Auditing")

    def recipient_legal_and_other(
        self,
        page,
        reporter_type="business",
    ):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        page.get_by_label("Professional and business").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Auditing").check()
        self.recipient(page, "Legal advisory")


class LicensingGroundsBase(PlaywrightTestBase):
    def licensing_grounds_simple(self, page):
        page.get_by_label("What is your purpose for").fill("Test purpose")
        page.get_by_role("button", name="Continue").click()

        # now we're on the upload documents page
        expect(page).to_have_url(re.compile(r".*/upload-documents"))
        page.get_by_test_id("upload-documents-continue").click()
        # page.get_by_role("link", name="Continue").click()


@pytest.fixture(autouse=True)
def patched_send_email(monkeypatch):
    """We don't want to send emails when running front-end tests"""
    mock_notifications_api_client = mock.create_autospec(notifications_python_client.notifications.NotificationsAPIClient)
    monkeypatch.setattr(notifier, "NotificationsAPIClient", mock_notifications_api_client)


@pytest.fixture
def patched_clean_document(monkeypatch):
    mock_document = MagicMock()
    mock_document.readline.side_effect = VirusFoundInFileException
    original_clean_document = UploadDocumentsForm.clean_document

    def mock_clean_document(self):
        self.cleaned_data["document"] = [mock_document]
        return original_clean_document(self)

    monkeypatch.setattr(UploadDocumentsForm, "clean_document", mock_clean_document)
