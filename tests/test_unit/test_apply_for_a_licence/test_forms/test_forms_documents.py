from unittest.mock import patch

from apply_for_a_licence.forms import forms_documents as forms
from django.core.files.uploadedfile import SimpleUploadedFile


class TestUploadDocumentsForm:
    class MockAllSessionFiles:
        def __init__(self, length: int = 0):
            self.length = length
            super().__init__()

        def __len__(self):
            return self.length

    def test_valid(self, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    good_file,
                ]
            },
            request=request_object,
        )
        assert form.is_valid()

    def test_invalid_mimetype(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"GIF8")
        bad_file.original_name = "bad.gif"

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "invalid_file_type"

    def test_invalid_extension(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"%PDF-test_pdf")
        bad_file.original_name = "bad.gif"

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "invalid_file_type"

    def test_too_large(self, request_object):
        large_file = SimpleUploadedFile("large.pdf", b"%PDF-test_pdf")
        large_file.size = 9999999999

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    large_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "too_large"

    @patch("apply_for_a_licence.forms.forms_documents.get_all_session_files", return_value=MockAllSessionFiles(length=10))
    def test_too_many_uploaded(self, mocked_get_all_session_files, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    good_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "too_many"

    def test_invalid_extension_file_name_escaped(self, request_object):
        bad_file = SimpleUploadedFile("<img src=xonerror=alert(document.domain)>gif.gif", b"GIF8")
        bad_file.original_name = "<img src=xonerror=alert(document.domain)>gif.gif"

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert (
            form.errors.as_data()["document"][0].message
            == "<img src=xonerror=alert(document.domain)>gif.gif cannot be uploaded.\n\nThe selected file must be a "
            "DOC, DOCX, ODT, FODT, XLS, XLSX, ODS, FODS, PPT, PPTX, ODP, FODP, PDF, TXT, CSV, "
            "ZIP, HTML, JPEG, JPG or PNG"
        )
