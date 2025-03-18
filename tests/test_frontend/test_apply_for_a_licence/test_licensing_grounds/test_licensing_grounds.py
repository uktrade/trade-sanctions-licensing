import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    AboutTheServicesBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)
from tests.test_frontend.fixtures.data import LEGAL_GROUNDS_HEADERS


class TestLicensingGrounds(StartBase, AboutTheServicesBase, ProviderBase, RecipientBase):
    """Tests for each of the outcomes based on which recipient is chosen"""

    def test_legal(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.professional_and_business_service(self.page, pbs_services=["Legal advisory"])
        self.page.get_by_role("link", name="Your purpose for providing").click()
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_only"])
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/services-purpose"))
        self.page.get_by_label("What is your purpose").fill("Test purpose")
        self.page.get_by_role("button", name="Continue").click()
        self.recipient(self.page)
        self.no_more_additions(self.page)
        self.check_your_answers(self.page, type="business", service="Professional and business services (Russia)")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)

    def test_non_legal(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.professional_and_business_service(self.page, pbs_services=["Accounting"])
        self.page.get_by_role("link", name="Your purpose for providing").click()
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["non_legal"])
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/services-purpose"))
        self.page.get_by_label("What is your purpose").fill("Test purpose")
        self.page.get_by_role("button", name="Continue").click()
        self.recipient(self.page)
        self.no_more_additions(self.page)
        self.check_your_answers(self.page, type="business", service="Professional and business services (Russia)")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)

    def test_legal_and_other(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.professional_and_business_service(self.page, pbs_services=["Legal advisory", "Accounting"])
        self.page.get_by_role("link", name="Your purpose for providing").click()
        expect(self.page).to_have_url(re.compile(r".*/licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_only"])
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/other-licensing-grounds"))
        expect(self.page).to_have_title(LEGAL_GROUNDS_HEADERS["legal_excluded"])
        self.page.get_by_label("The delivery of humanitarian").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/services-purpose"))
        self.page.get_by_label("What is your purpose").fill("Test purpose")
        self.page.get_by_role("button", name="Continue").click()
        self.recipient(self.page)
        self.no_more_additions(self.page)
        self.check_your_answers(self.page, type="business", service="Professional and business services (Russia)")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)
