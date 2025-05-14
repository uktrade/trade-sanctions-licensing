import re

from django.urls import reverse
from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    AboutTheServicesBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestAddMyself(StartBase, ProviderBase, RecipientBase, AboutTheServicesBase):
    """Tests for the myself journey"""

    def test_located_in_uk(self):
        self.start_new_application()
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.no_more_additions(self.page)
        self.previous_licence(self.page)
        self.simple_about_the_service_task(self.page)
        self.recipient(self.page)
        self.no_more_additions(self.page)
        self.check_your_answers(self.page, type="myself")
        expect(self.page.get_by_test_id("who-the-licence-covers-name")).to_have_text("Test first name Test last name")
        expect(self.page.get_by_test_id("who-the-licence-covers-connection")).to_have_text("UK national located in the UK")
        expect(self.page.get_by_test_id("who-the-licence-covers-address")).to_have_text("A1, Town, AA0 0AA, United Kingdom")
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        self.check_submission_complete_page(self.page)

    def test_add_another_individual_and_remove(self):
        self.start_new_application()
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page, first_name="new_person_first", last_name="test")
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        expect(self.page.get_by_role("heading", name="You've added yourself plus 1 individual to the licence")).to_be_visible()
        self.page.get_by_role("button", name="Remove Individual 1").click()
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        expect(self.page.get_by_role("heading", name="You've added yourself to the licence")).to_be_visible()

    def test_draft_individual_has_text(self):
        self.start_new_application()
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Skip for now and return to").click()
        # get licence_id from url
        page_url = self.page.url
        licence_id = page_url.rsplit("/")[-1]
        self.go_to_path(reverse("yourself_and_individual_added", kwargs={"licence_pk": licence_id}))
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        expect(self.page.get_by_role("heading", name="You've added yourself plus 1 individual to the licence")).to_be_visible()
        expect(self.page.get_by_test_id("individual-address-1")).to_have_text("Not yet added")
        expect(self.page.get_by_test_id("individual-nationality-location-1")).to_have_text("Not yet added")
        expect(self.page.get_by_test_id("individual-name-1")).to_have_text("Not yet added")

    def test_draft_yourself_has_text(self):
        self.start_new_application()
        self.myself(self.page)
        # get licence_id from url
        page_url = self.page.url
        licence_id = page_url.rsplit("/")[-1].split("?")[0]
        self.your_details(self.page, "myself")
        self.go_to_path(reverse("yourself_and_individual_added", kwargs={"licence_pk": licence_id}))
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        expect(self.page.get_by_role("heading", name="You've added yourself to the licence")).to_be_visible()
        expect(self.page.get_by_test_id("yourself-address")).to_have_text("Not yet added")
