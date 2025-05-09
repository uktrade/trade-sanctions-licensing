from unittest.mock import patch

import pytest
from apply_for_a_licence.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.factories import LicenceFactory


@pytest.mark.django_db
class TestDocumentModel:
    @patch("apply_for_a_licence.models.store_document_in_permanent_bucket", return_value=None)
    def test_save_documents(self, mocked_store_document_in_permanent_bucket):
        licence = LicenceFactory()
        Document.objects.create(
            licence=licence, temp_file=SimpleUploadedFile("test.png", b"file_content"), original_file_name="test.png"
        )
        Document.objects.create(
            licence=licence, temp_file=SimpleUploadedFile("test.pdf", b"file_content"), original_file_name="test.pdf"
        )
        documents = Document.objects.filter(licence=licence.id)
        for doc in documents:
            assert str(licence.id) in doc.temp_file.name
            assert not doc.file

        Document.save_documents(licence=licence)
        documents = Document.objects.filter(licence=licence.id)
        for doc in documents:
            assert str(licence.id) in doc.file.name
            assert not doc.temp_file
