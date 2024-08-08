import logging
from unittest.mock import patch

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from utils.s3 import get_user_uploaded_files

logger = logging.getLogger(__name__)


@patch("apply_for_a_licence.forms.get_all_session_files", new=lambda x, y: [])
@patch("apply_for_a_licence.views.get_all_session_files", new=lambda x, y: [])
class TestDocumentUploadView:
    def test_successful_post(self, afal_client):
        response = afal_client.post(
            reverse("upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 201

    def test_file_names_stored_in_cache(self, afal_client):
        cache.clear()
        assert not get_user_uploaded_files(afal_client.session)
        afal_client.post(
            reverse("upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert get_user_uploaded_files(afal_client.session) == ["test.png"]

    def test_unsuccessful_post(self, afal_client):
        response = afal_client.post(
            reverse("upload_documents"),
            data={"document": SimpleUploadedFile("bad.gif", b"GIF8")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        response = response.json()
        assert response["success"] is False
        assert "it is not a valid file type" in response["error"]
        assert response["file_name"].split("/")[1] == "bad.gif"
        assert "file_uploads" not in afal_client.session

    def test_non_ajax_successful_post(self, afal_client):
        response = afal_client.post(
            reverse("upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            follow=True,
        )
        assert response.status_code == 200
        assert response.request["PATH_INFO"] == "/apply-for-a-licence/check_your_answers"

    def test_non_ajax_unsuccessful_post(self, afal_client):
        response = afal_client.post(
            reverse("upload_documents"),
            data={"document": SimpleUploadedFile("bad.gif", b"GIF8")},
            follow=True,
        )
        assert response.status_code == 200
        form = response.context["form"]
        assert not form.is_valid()
        assert "govuk-error-summary" in response.content.decode()
        assert "it is not a valid file type" in response.content.decode()


@patch("apply_for_a_licence.views.TemporaryDocumentStorage.delete")
class TestDeleteDocumentsView:
    def test_successful_post(self, mocked_temporary_document_storage, afal_client):
        response = afal_client.post(
            reverse("delete_documents") + "?file_name=test.png",
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}
        assert mocked_temporary_document_storage.call_count == 1
        assert mocked_temporary_document_storage.assert_called_once_with("test.png")

    def test_unsuccessful_post(self, mocked_temporary_document_storage, afal_client):
        response = afal_client.post(
            reverse("delete_documents"),
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 400
        assert response.json() == {"success": False}
        assert mocked_temporary_document_storage.call_count == 0


class TestDownloadDocumentMiddleman:

    @patch("apply_for_a_licence.views.get_user_uploaded_files", return_value=["test.png"])
    @patch("apply_for_a_licence.views.generate_presigned_url", return_value="www.example.com")
    def test_download_document_middleman(self, mocked_uploaded_files, mocked_url, caplog, afal_client):
        with caplog.at_level(logging.INFO, logger="apply_for_a_licence.views"):
            response = afal_client.get(reverse("download_document", kwargs={"file_name": "test.png"}))
            assert "User is downloading file: test.png" in caplog.text
        assert response.status_code == 302
        assert response.url == "www.example.com"

    @patch("apply_for_a_licence.views.get_user_uploaded_files", return_value=["hello.png"])
    def test_download_document_middleman_not_in_cache(self, mocked_uploaded_files, afal_client):
        response = afal_client.get(reverse("download_document", kwargs={"file_name": "test.png"}))
        assert response.status_code == 404