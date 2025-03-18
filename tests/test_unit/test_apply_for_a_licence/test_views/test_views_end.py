from unittest.mock import patch

from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from tests.factories import IndividualFactory, OrganisationFactory


class TestCheckYourAnswersView:
    def test_get_context_data(self, authenticated_al_client_with_licence, licence_application):
        OrganisationFactory.create_batch(3, licence=licence_application, type_of_relationship="recipient")
        OrganisationFactory.create_batch(3, licence=licence_application, type_of_relationship="business")
        IndividualFactory.create_batch(3, licence=licence_application, is_applicant=False)
        applicant_individual = IndividualFactory(licence=licence_application, is_applicant=True)
        business_individual_works_for = OrganisationFactory(licence=licence_application, type_of_relationship="named_individuals")

        response = authenticated_al_client_with_licence.get(reverse("check_your_answers"))
        assert response.status_code == 200

        assert response.context["licence"] == licence_application
        assert len(response.context["recipients"]) == 3
        assert len(response.context["businesses"]) == 3
        assert len(response.context["individuals"]) == 3
        assert response.context["applicant_individual"] == applicant_individual
        assert response.context["business_individual_works_for"] == business_individual_works_for
        assert response.context["new_individual_uuid"]
        assert response.context["new_business_uuid"]


@patch("apply_for_a_licence.views.views_end.send_email")
class TestDeclarationView:
    def test_licence_application_status_is_changed(
        self, patched_send_email, authenticated_al_client_with_licence, licence_application
    ):
        licence_application.status = "draft"
        licence_application.submitted_at = None
        licence_application.reference = ""
        licence_application.save()

        response = authenticated_al_client_with_licence.post(reverse("declaration"), data={"declaration": True})
        assert response.status_code == 302
        licence_application.refresh_from_db()
        assert licence_application.status == "submitted"
        assert licence_application.reference
        assert licence_application.submitted_at

    @override_settings(NEW_APPLICATION_ALERT_RECIPIENTS=["test1@example.com"])
    @patch("apply_for_a_licence.views.views_end.get_view_a_licence_application_url")
    def test_send_emails(
        self,
        patched_get_view_a_licence_application_url,
        patched_send_email,
        authenticated_al_client_with_licence,
        licence_application,
    ):
        patched_get_view_a_licence_application_url.return_value = "http://test.com"
        authenticated_al_client_with_licence.post(reverse("declaration"), data={"declaration": True})
        licence_application.refresh_from_db()
        assert patched_send_email.call_count == 2
        patched_send_email.assert_any_call(
            email=licence_application.user.email,
            template_id=settings.PUBLIC_USER_NEW_APPLICATION_TEMPLATE_ID,
            context={"name": licence_application.applicant_full_name, "application_number": licence_application.reference},
        )
        patched_send_email.assert_any_call(
            email="test1@example.com",
            template_id=settings.OTSI_NEW_APPLICATION_TEMPLATE_ID,
            context={"application_number": licence_application.reference, "url": "http://test.com"},
        )
