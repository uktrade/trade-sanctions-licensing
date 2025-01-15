from django.urls import reverse


class TestPreviousLicenceView:
    def test_get_context_data(self, authenticated_al_client):
        response = authenticated_al_client.get(reverse("previous_licence"))
        assert response.context["page_title"] == (
            "Have any of the businesses you've added held a licence before to provide "
            "any sanctioned services or export any sanctioned goods?"
        )
