import logging
from unittest.mock import patch

from apply_for_a_licence.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from tests.factories import LicenceFactory

logger = logging.getLogger(__name__)


class TestDocumentUploadView:
    def test_successful_post(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.post(
            reverse("upload_documents"),
            data={"file": SimpleUploadedFile("test.png", b"file_content")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 201

    def test_unsuccessful_post(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.post(
            reverse("upload_documents"),
            data={"file": SimpleUploadedFile("bad.gif", b"GIF8")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        response = response.json()
        assert response["success"] is False
        assert (
            "The selected file must be a DOC, DOCX, ODT, FODT, XLS, XLSX, ODS, FODS, "
            "PPT, PPTX, ODP, FODP, PDF, TXT, CSV, ZIP, HTML, JPEG, JPG or PNG" in response["error"]
        )
        assert response["file_name"] == "bad.gif"

    def test_non_ajax_successful_post(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.post(
            reverse("upload_documents"),
            data={"file": SimpleUploadedFile("test.png", b"file_content")},
            follow=True,
        )
        assert response.status_code == 200
        assert response.request["PATH_INFO"] == "/apply/check-your-answers"

    def test_non_ajax_unsuccessful_post(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.post(
            reverse("upload_documents"),
            data={"file": SimpleUploadedFile("bad.gif", b"GIF8")},
            follow=True,
        )
        assert response.status_code == 200
        form = response.context["form"]
        assert not form.is_valid()
        assert "govuk-error-summary" in response.content.decode()
        assert (
            "The selected file must be a DOC, DOCX, ODT, FODT, XLS, XLSX, ODS, FODS, PPT, PPTX, "
            "ODP, FODP, PDF, TXT, CSV, ZIP, HTML, JPEG, JPG or PNG" in response.content.decode()
        )


@patch("apply_for_a_licence.views.views_documents.TemporaryDocumentStorage.delete")
class TestDeleteDocumentsView:
    def test_successful_post(self, mocked_temporary_document_storage, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("delete_documents") + "?file_name=test.png",
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}
        assert mocked_temporary_document_storage.call_count == 1
        args, kwargs = mocked_temporary_document_storage.call_args
        assert f"{authenticated_al_client.session.session_key}/test.png" in args

    def test_unsuccessful_post(self, mocked_temporary_document_storage, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("delete_documents"),
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 400
        assert response.json() == {"success": False}
        assert mocked_temporary_document_storage.call_count == 0


class TestDownloadDocumentMiddleman:
    def test_download_document_middleman(self, caplog, authenticated_al_client_with_licence, licence_application):
        document_object = Document.objects.create(
            licence=licence_application, file="test1231242342.png", original_file_name="test.png"
        )

        with caplog.at_level(logging.INFO, logger="apply_for_a_licence.views"):
            response = authenticated_al_client_with_licence.get(reverse("download_document", kwargs={"pk": document_object.pk}))
            assert f"User apply_test_user@example.com has downloaded file: test.png (PK {document_object.pk})" in caplog.text
        assert response.status_code == 302
        assert "permanent-document-bucket" in response.url

    def test_download_document_middleman_doesnt_belong_to_you(self, authenticated_al_client_with_licence):
        licence_application = LicenceFactory(user=None)
        document_object = Document.objects.create(
            licence=licence_application, file="test1231242342.png", original_file_name="test.png"
        )
        response = authenticated_al_client_with_licence.get(reverse("download_document", kwargs={"pk": document_object.pk}))
        assert response.status_code == 404
