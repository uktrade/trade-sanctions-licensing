from apply_for_a_licence.choices import StatusChoices
from django.urls import reverse

from tests.factories import LicenceFactory


class TestApplicationListView:
    def test_get_queryset(self, vl_client_logged_in):
        LicenceFactory.create_batch(3, status=StatusChoices.submitted)
        response = vl_client_logged_in.get(reverse("view_a_licence:application_list"))
        objects = response.context["licence_list"]
        assert objects.count() == 3
        assert objects[0].created_at > objects[1].created_at > objects[2].created_at

    def test_draft_applications_not_included(self, vl_client_logged_in):
        LicenceFactory.create(status=StatusChoices.draft)
        submitted_app = LicenceFactory.create(status=StatusChoices.submitted)
        response = vl_client_logged_in.get(reverse("view_a_licence:application_list"))
        objects = response.context["licence_list"]
        assert objects.count() == 1
        assert objects.get() == submitted_app
