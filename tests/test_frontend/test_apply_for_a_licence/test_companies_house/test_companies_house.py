import re
from unittest.mock import patch

from playwright.sync_api import expect

from tests.test_frontend.conftest import ProviderBase, StartBase


class TestCompaniesHouse(StartBase, ProviderBase):
    """Tests for the companies house journey"""

    def test_companies_house_number_unknown(self):
        self.start_new_application()
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.your_details(self.page)
        self.page.get_by_label("Yes", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where-business-located"))

    @patch(
        "apply_for_a_licence.forms.forms_business.get_details_from_companies_house",
        return_value={
            "company_name": "Test Company",
            "company_number": "12345678",
            "registered_office_address": {
                "address_line_1": "1 Test Street",
                "address_line_2": "Test Town",
                "town_or_city": "Test City",
                "postcode": "TE5 7PC",
                "country": "United Kingdom",
            },
        },
    )
    def test_companies_house_number_incorrect(self, patched_companies_house):
        self.start_new_application()
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.your_details(self.page)
        self.page.get_by_label("Yes", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Yes", exact=True).check()
        number_input = self.page.get_by_label("Registered company number")  # Wait 10 seconds for popup to load
        number_input.wait_for(state="visible", timeout=10000)
        number_input.fill("0")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("link", name="Number not recognised with")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/registered-company-number"))

    @patch(
        "apply_for_a_licence.forms.forms_business.get_details_from_companies_house",
        return_value={
            "company_name": "Test Company",
            "company_number": "12345678",
            "registered_office_address": {
                "address_line_1": "1 Test Street",
                "address_line_2": "Test Town",
                "town_or_city": "Test City",
                "postcode": "TE5 7PC",
                "country": "United Kingdom",
            },
        },
    )
    def test_companies_house_number(self, patched_companies_house):
        self.start_new_application()
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.your_details(self.page)
        self.page.get_by_label("Yes", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Yes", exact=True).check()
        number_input = self.page.get_by_label("Registered company number")  # Wait 10 seconds for popup to load
        number_input.wait_for(state="visible", timeout=10000)
        number_input.fill("12345678")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="Check company details")).to_be_visible()
        expect(self.page.get_by_text("12345678")).to_be_visible()

    @patch(
        "apply_for_a_licence.forms.forms_business.get_details_from_companies_house",
        return_value={
            "company_name": "Test Company",
            "company_number": "12345678",
            "registered_office_address": {
                "address_line_1": "1 Test Street",
                "address_line_2": "Test Town",
                "town_or_city": "Test City",
                "postcode": "TE5 7PC",
                "country": "United Kingdom",
            },
        },
    )
    def test_back_button_on_check_companies_details(self, patched_companies_house):
        self.start_new_application()
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.your_details(self.page)
        self.page.get_by_label("Yes", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Yes", exact=True).check()
        number_input = self.page.get_by_label("Registered company number")  # Wait 10 seconds for popup to load
        number_input.wait_for(state="visible", timeout=10000)
        number_input.fill("12345678")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="Check company details")).to_be_visible()
        expect(self.page.get_by_text("12345678")).to_be_visible()
        self.page.go_back()
        self.page.go_back()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(self.page, "business")
        expect(self.page.get_by_role("heading", name="You've added 1 business")).to_be_visible()
