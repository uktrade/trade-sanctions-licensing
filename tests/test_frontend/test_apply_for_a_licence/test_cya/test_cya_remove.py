import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestCYARemove(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Test removing an entity on Check Your Answers."""

    def test_cya_remove_businesses_and_recipients(self):
        self.start_new_application()
        self.business_third_party(self.page)
        self.provider_business_located_in_uk(self.page)
        # Add 3 businesses
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page)
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page)
        self.no_more_additions(self.page)

        # Add 3 Recipients
        self.recipient_simple(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page, "recipient")
        self.page.get_by_label("What is the relationship").fill("Test relationship")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(self.page, "recipient")
        self.page.get_by_label("What is the relationship").fill("Test relationship")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)

        # Delete businesses.
        self.page.get_by_role("button", name="Remove Business 3").click()
        expect(self.page.get_by_role("button", name="Remove Business 1")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Business 2")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Business 3")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        self.page.get_by_role("button", name="Remove Business 1").click()
        expect(self.page.get_by_role("button", name="Remove Business 1")).not_to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Business 2")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))

        # Delete recipients
        self.page.get_by_role("button", name="Remove Recipient 3").click()
        expect(self.page.get_by_role("button", name="Remove Recipient 1")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Recipient 2")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Recipient 3")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        self.page.get_by_role("button", name="Remove Recipient 1").click()
        expect(self.page.get_by_role("button", name="Remove Recipient 1")).not_to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Recipient 2")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))

    def test_cya_remove_individual_journey(self):
        self.start_new_application()
        self.individual_third_party(self.page)
        # Add 3 individuals.

        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-individual"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page)
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page)
        self.no_more_additions(self.page)
        self.recipient_simple(self.page, "individual")
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)
        self.check_your_answers(self.page, type="individual")
        # Delete individuals.

        self.page.get_by_role("button", name="Remove Individual 3").click()
        expect(self.page.get_by_role("button", name="Remove Individual 1")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Individual 2")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Individual 3")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        self.page.get_by_role("button", name="Remove Individual 1").click()
        expect(self.page.get_by_role("button", name="Remove Individual 1")).not_to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Individual 2")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)

    def test_cya_remove_myself_journey(self):
        self.start_new_application()
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        # Add 2 Individuals
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page)
        self.no_more_additions(self.page)
        self.recipient_simple(self.page, "myself")
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)
        self.check_your_answers(self.page, type="myself")

        # Delete all individuals
        expect(self.page.get_by_role("button", name="Remove Individual 1")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Individual 2")).to_be_visible()
        self.page.get_by_role("button", name="Remove Individual 1").click()
        expect(self.page.get_by_role("button", name="Remove Individual 1")).to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Individual 2")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        self.page.get_by_role("button", name="Remove Individual 1").click()
        expect(self.page.get_by_role("button", name="Remove Individual 1")).not_to_be_visible()
        expect(self.page.get_by_role("button", name="Remove Individual 2")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/check-your-answers"))
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)
