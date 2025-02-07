from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

from django_app.apply_for_a_licence.views.views_end import DownloadPDFView
from tests.conftest import LicenceFactory


@pytest.mark.django_db
@patch("apply_for_a_licence.views.views_end.SaveToDB", return_value=MagicMock())
@patch("apply_for_a_licence.views.views_end.send_email", new=MagicMock())
class TestDeclarationView:
    """We're just testing the view logic here, not the chunky save_to_db stuff"""

    @patch("apply_for_a_licence.views.views_end.get_all_cleaned_data")
    def test_is_individual(self, patched_clean_data, patched_save_to_db, authenticated_al_client, licence_request_object):
        licence_request_object.session["start"]["who_do_you_want_the_licence_to_cover"] = "individual"
        licence_request_object.session.save()
        patched_clean_data.return_value = licence_request_object.session
        patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()

        authenticated_al_client.post(reverse("declaration"), data={"declaration": "on"})
        args, kwargs = patched_save_to_db.call_args
        assert kwargs.get("is_individual") is True
        assert kwargs.get("is_third_party") is False
        assert kwargs.get("is_on_companies_house") is False
        assert patched_save_to_db.return_value.save_individuals.called

    @patch("apply_for_a_licence.views.views_end.get_all_cleaned_data")
    def test_is_myself(self, patched_clean_data, patched_save_to_db, authenticated_al_client, licence_request_object):
        licence_request_object.session["start"]["who_do_you_want_the_licence_to_cover"] = "myself"
        licence_request_object.session.save()
        patched_clean_data.return_value = licence_request_object.session
        patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()

        authenticated_al_client.post(reverse("declaration"), data={"declaration": "on"})
        args, kwargs = patched_save_to_db.call_args
        assert kwargs.get("is_individual") is False
        assert kwargs.get("is_third_party") is False
        assert kwargs.get("is_on_companies_house") is False
        assert patched_save_to_db.return_value.save_individuals.called

    @patch("apply_for_a_licence.views.views_end.get_all_cleaned_data")
    def test_is_on_companies_house(self, patched_clean_data, patched_save_to_db, authenticated_al_client, licence_request_object):
        licence_request_object.session["start"]["who_do_you_want_the_licence_to_cover"] = "business"
        licence_request_object.session["is_the_business_registered_with_companies_house"][
            "business_registered_on_companies_house"
        ] = "yes"
        licence_request_object.session["do_you_know_the_registered_company_number"][
            "do_you_know_the_registered_company_number"
        ] = "yes"
        licence_request_object.session.save()
        patched_clean_data.return_value = licence_request_object.session

        patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()

        authenticated_al_client.post(reverse("declaration"), data={"declaration": "on"})
        args, kwargs = patched_save_to_db.call_args
        assert kwargs.get("is_on_companies_house") is True
        assert kwargs.get("is_individual") is False

    @patch("apply_for_a_licence.views.views_end.get_all_cleaned_data")
    def test_is_third_party(self, patched_clean_data, patched_save_to_db, authenticated_al_client, licence_request_object):
        licence_request_object.session["start"]["who_do_you_want_the_licence_to_cover"] = "business"
        licence_request_object.session["are_you_third_party"]["are_you_applying_on_behalf_of_someone_else"] = "True"
        licence_request_object.session.save()
        patched_clean_data.return_value = licence_request_object.session
        patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()

        authenticated_al_client.post(reverse("declaration"), data={"declaration": "on"})
        args, kwargs = patched_save_to_db.call_args
        assert kwargs.get("is_on_companies_house") is False
        assert kwargs.get("is_individual") is False
        assert kwargs.get("is_third_party") is True


class TestDownloadPDFView:
    @patch("apply_for_a_licence.models.Licence.objects.get", return_value=MagicMock())
    @patch("apply_for_a_licence.views.views_end.BaseDownloadPDFView", return_value=MagicMock())
    def test_successful_get(self, mock_download, mock_licence):
        print(mock_licence)
        test_reference = "DE1234"
        request = RequestFactory().get("?reference=" + test_reference)

        view = DownloadPDFView()
        view.setup(request, reference=test_reference)
        response = view.get(request, reference=test_reference)

        expected_response = HttpResponse(status=200)
        assert response.status_code == expected_response.status_code
        mock_licence.assert_called_with(reference=test_reference)
