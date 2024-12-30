from apply_for_a_licence.choices import (
    LicensingGroundsChoices,
    ProfessionalOrBusinessServicesChoices,
    TypeOfServicesChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
)
from django.urls import reverse
from playwright.sync_api import expect

from tests.factories import LicenceFactory
from tests.test_frontend.test_view_a_licence.conftest import PlaywrightTestBase


class TestViewALicenceApplicationView(PlaywrightTestBase):
    def test_legal_grounds_legal_advisory(self):
        licence = LicenceFactory.create(
            who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value,
            type_of_service=TypeOfServicesChoices.professional_and_business.value,
            professional_or_business_services=[
                ProfessionalOrBusinessServicesChoices.legal_advisory.value,
                ProfessionalOrBusinessServicesChoices.architectural.value,
            ],
            licensing_grounds=[LicensingGroundsChoices.energy.value],
            licensing_grounds_legal_advisory=[LicensingGroundsChoices.food.value, LicensingGroundsChoices.safety.value],
        )
        licence.assign_reference()
        licence.save()
        self.page.goto(self.base_url + reverse("view_a_licence:view_application", kwargs={"reference": licence.reference}))

        conditional_box = self.page.get_by_test_id("licensing-grounds-legal-advisory-box")
        expect(conditional_box).to_be_visible()
        assert "Licensing grounds (excluding legal advisory)" in conditional_box.text_content()
        assert LicensingGroundsChoices.food.label in conditional_box.text_content()
        assert LicensingGroundsChoices.safety.value in conditional_box.text_content()

        # now checking without legal advisory
        licence = LicenceFactory.create(
            who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value,
            type_of_service=TypeOfServicesChoices.professional_and_business.value,
            professional_or_business_services=[ProfessionalOrBusinessServicesChoices.architectural.value],
            licensing_grounds=[LicensingGroundsChoices.energy.value],
            licensing_grounds_legal_advisory=None,
        )
        licence.assign_reference()
        licence.save()
        self.page.goto(self.base_url + reverse("view_a_licence:view_application", kwargs={"reference": licence.reference}))

        assert self.page.get_by_test_id("licensing-grounds-legal-advisory-box").count() == 0
