from django.urls import reverse

from tests.factories import LicenceFactory


class TestApplicationListView:
    def test_get_queryset(self, vl_client_logged_in):
        LicenceFactory.create_batch(3)
        response = vl_client_logged_in.get(reverse("view_a_licence:application_list"))
        objects = response.context["licence_list"]
        assert objects.count() == 3
        assert objects[0].created_at > objects[1].created_at > objects[2].created_at
