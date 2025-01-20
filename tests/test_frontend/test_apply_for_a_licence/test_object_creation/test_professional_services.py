from apply_for_a_licence import choices
from apply_for_a_licence.models import Licence

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestProfessionalServices(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Tests that the professional services are saved correctly"""

    def test_professional_business_services_saved(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        self.no_more_additions(self.page)
        self.recipient_legal_and_other(self.page)
        self.no_more_additions(self.page)
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Civil society activities that").check()
        self.page.get_by_role("button", name="Continue").click()
        self.licensing_grounds_simple(self.page)
        self.page.get_by_test_id("continue_button").click()
        self.declaration_and_complete_page(self.page)

        new_licence_object = Licence.objects.first()
        assert new_licence_object.professional_or_business_services == [
            choices.ProfessionalOrBusinessServicesChoices.auditing.value,
            choices.ProfessionalOrBusinessServicesChoices.legal_advisory.value,
        ]
