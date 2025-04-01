import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)
from tests.test_frontend.fixtures.data import LEGAL_GROUNDS_HEADERS


class TestLicensingGrounds(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Tests for each of the outcomes based on which recipient is chosen"""

    def test_legal(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_legal(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_only"])
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/services-purpose"))
        self.page.get_by_label("What is your purpose").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/upload-documents"))

    def test_non_legal(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_non_legal(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["non_legal"])
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/services-purpose"))
        self.page.get_by_label("What is your purpose").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/upload-documents"))

    def test_legal_and_other(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_legal_and_other(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_only"])
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/other-licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_excluded"])
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/services-purpose"))
        self.page.get_by_label("What is your purpose").fill("test")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/upload-documents"))

    def test_unknown_or_no_grounds_clears_other_grounds(self):
        self.page.goto(self.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_legal_and_other(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        self.page.get_by_label("Services in connection with").check()
        self.page.get_by_label("I do not know").check()
        expect(self.page.get_by_label("Services in connection with").not_to_be_checked())
        expect(self.page.get_by_label("I do not know").to_be_checked())
        self.page.get_by_label("Services in connection with").check()
        self.page.get_by_label("Services required to enable").check()
        self.page.get_by_label("Medical and pharmaceutical").check()
        expect(self.page.get_by_label("Services in connection with").to_be_checked())
        expect(self.page.get_by_label("Services required to enable").to_be_checked())
        expect(self.page.get_by_label("Medical and pharmaceutical").to_be_checked())
        expect(self.page.get_by_label("I do not know").not_to_be_checked())
        self.page.get_by_label("I do not know").check()
        self.page.get_by_label("None of these").check()
        expect(self.page.get_by_label("Services in connection with").not_to_be_checked())
        expect(self.page.get_by_label("Services required to enable").not_to_be_checked())
        expect(self.page.get_by_label("Medical and pharmaceutical").not_to_be_checked())
        expect(self.page.get_by_label("I do not know").not_to_be_checked())
        expect(self.page.get_by_label("None of these").to_be_checked())
