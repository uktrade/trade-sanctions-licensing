import re

from apply_for_a_licence import choices
from apply_for_a_licence.models import Licence
from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    AboutTheServicesBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)
from tests.test_frontend.fixtures.data import LEGAL_GROUNDS_HEADERS


class TestProfessionalServices(StartBase, AboutTheServicesBase, ProviderBase, RecipientBase):
    """Tests that the professional services are saved correctly"""

    def test_professional_business_services_saved(self):
        reference = self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.professional_and_business_service(self.page, pbs_services=["Auditing", "Legal"])
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

        licence_object = Licence.objects.get(submitter_reference=reference)
        assert licence_object.professional_or_business_services == [
            choices.ProfessionalOrBusinessServicesChoices.auditing.value,
            choices.ProfessionalOrBusinessServicesChoices.legal_advisory.value,
        ]
