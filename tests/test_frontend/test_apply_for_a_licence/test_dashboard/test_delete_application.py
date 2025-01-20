import re

from apply_for_a_licence.models import Licence
from django.contrib.auth.models import User
from playwright.sync_api import expect

from tests.factories import LicenceFactory
from tests.test_frontend.conftest import PlaywrightTestBase


class TestDeleteApplication(PlaywrightTestBase):
    def test_delete_application(self):
        user = User.objects.get(email="apply_test_user@example.com")
        licence = LicenceFactory(user=user, status="draft")
        pk = licence.pk
        assert Licence.objects.filter(pk=pk).exists()

        self.start_new_application()
        self.page.get_by_role("link", name="Delete draft").click()
        self.page.get_by_role("button", name="Delete this application").click()

        assert not Licence.objects.filter(pk=pk).exists()


class TestNewApplicationView(PlaywrightTestBase):
    def test_start_new_application(self):
        assert Licence.objects.count() == 0
        self.start_new_application()
        self.page.get_by_role("link", name="Start a new application").click()
        self.page.get_by_label("Your application name").click()
        self.page.get_by_label("Your application name").fill("test reference")
        self.page.get_by_role("button", name="Save and continue").click()

        expect(self.page).to_have_url(re.compile(r".*/start"))
        assert Licence.objects.count() == 1
        licence = Licence.objects.first()

        user = User.objects.get(email="apply_test_user@example.com")

        assert licence.submitter_reference == "test reference"
        assert licence.user == user
        assert licence.status == "draft"
