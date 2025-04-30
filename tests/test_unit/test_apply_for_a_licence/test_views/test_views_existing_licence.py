from django.urls import reverse


class TestPreviousLicenceView:
    def test_get_context_data(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.get(
            reverse("previous_licence", kwargs={"licence_pk": licence_application.id})
        )
        assert response.context["page_title"] == (
            "Have any of the businesses you've added held a licence before to provide "
            "any sanctioned services or export any sanctioned goods?"
        )

    def test_success_url(self, authenticated_al_client_with_licence, licence_application):
        response = authenticated_al_client_with_licence.post(
            reverse("previous_licence", kwargs={"licence_pk": licence_application.id}),
            data={"held_existing_licence": "no"},
        )
        assert response.url == reverse("tasklist", kwargs={"licence_pk": licence_application.id})
