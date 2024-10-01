import os

from django.conf import settings
from django.test.testcases import TransactionTestCase
from playwright.sync_api import sync_playwright

from . import data


class PlaywrightTestBase(TransactionTestCase):
    create_new_test_breach = True
    base_url = settings.BASE_FRONTEND_TESTING_URL

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=settings.HEADLESS)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

        super().tearDownClass()

    def setUp(self) -> None:
        """Create a new page for each test"""
        self.page = self.browser.new_page()

    def tearDown(self) -> None:
        """Close the page after each test"""
        self.page.close()

    @classmethod
    def get_form_step_page(cls, form_step):
        print(f"{cls.base_url}/{form_step}/")
        return f"{cls.base_url}/report_a_suspected_breach/{form_step}/"

    @classmethod
    def email_details(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_label("What is your email address?").click()
        page.get_by_label("What is your email address?").fill(details["email"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def verify_email(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_role("heading", name="We've sent you an email").click()
        page.get_by_label("Enter the 6 digit security").fill(details["verify_code"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def verify_email_details(cls, page, details=data.EMAIL_DETAILS):
        #
        # Email page
        #
        page = cls.email_details(page, details)
        #
        # Verify page
        #
        page = cls.verify_email(page, details)

        return page

    def fill_uk_address_details(cls, page, details=data.UK_ADDRESS_DETAILS):
        # UK Address Details Page
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill(details["name"])
        page.get_by_label("Name of business or person").press("Tab")
        page.get_by_label("Website address").fill(details["website"])
        page.get_by_label("Website address").press("Tab")
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Address line 1").press("Tab")
        page.get_by_label("Address line 2").fill(details["address_line_2"])
        page.get_by_label("Address line 2").press("Tab")
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("Town or city").press("Tab")
        page.get_by_label("County").fill(details["county"])
        page.get_by_label("County").press("Tab")
        page.get_by_label("Postcode").fill(details["postcode"])
        page.get_by_role("button", name="Continue").click()

        return page

    @classmethod
    def fill_non_uk_address_details(cls, page, details=data.NON_UK_ADDRESS_DETAILS):
        # NON UK Address Details Page
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill(details["name"])
        page.get_by_label("Name of business or person").press("Tab")
        page.get_by_label("Website address").fill(details["website"])
        page.get_by_label("Website address").press("Tab")
        page.get_by_label("Country").select_option(details["country"])
        page.get_by_label("Country").press("Tab")
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Address line 1").press("Tab")
        page.get_by_label("Address line 2").fill(details["address_line_2"])
        page.get_by_label("Address line 2").press("Tab")
        page.get_by_label("Address line 3").fill(details["address_line_3"])
        page.get_by_label("Address line 3").press("Tab")
        page.get_by_label("Address line 4").fill(details["address_line_4"])
        page.get_by_label("Address line 4").press("Tab")
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("Town or city").press("Tab")
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def declaration_and_complete_page(cls, page):
        #
        # Declaration Page
        #
        page.get_by_role("heading", name="Declaration").click()
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Continue").click()
        #
        # Complete Page
        #
        page.get_by_role("heading", name="Submission complete").click()
        page.get_by_text("Your reference number").click()
        page.get_by_role("heading", name="What happens next").click()
        page.get_by_text("We have sent you a").click()
        page.get_by_role("link", name="View and print your report").click()
        page.get_by_text("What did you think of this service? (takes 30 seconds)").click()
        page.get_by_role("link", name="What did you think of this").click()
        return page
