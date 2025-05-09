from apply_for_a_licence.forms import forms_documents as forms
from apply_for_a_licence.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile


class TestUploadDocumentsForm:
    class MockAllSessionFiles:
        def __init__(self, length: int = 0):
            self.length = length
            super().__init__()

        def __len__(self):
            return self.length

    def test_valid(self, licence, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")

        form = forms.UploadDocumentsForm(
            files={
                "file": [
                    good_file,
                ]
            },
            request=request_object,
            licence_object=licence,
        )
        assert form.is_valid()

    def test_invalid_mimetype(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"GIF8")
        bad_file.original_name = "bad.gif"

        form = forms.UploadDocumentsForm(
            files={
                "file": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "file" in form.errors
        assert form.errors.as_data()["file"][0].code == "invalid_file_type"

    def test_invalid_extension(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"%PDF-test_pdf")
        bad_file.original_name = "bad.gif"

        form = forms.UploadDocumentsForm(
            files={
                "file": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "file" in form.errors
        assert form.errors.as_data()["file"][0].code == "invalid_file_type"

    def test_too_large(self, licence, request_object):
        large_file = SimpleUploadedFile("large.pdf", b"%PDF-test_pdf")
        large_file.size = 9999999999

        form = forms.UploadDocumentsForm(
            files={
                "file": [
                    large_file,
                ]
            },
            request=request_object,
            licence_object=licence,
        )
        assert not form.is_valid()
        assert "file" in form.errors
        assert form.errors.as_data()["file"][0].code == "too_large"

    def test_too_many_uploaded(self, licence, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")
        for x in range(10):
            Document.objects.create(
                licence=licence,
                temp_file=SimpleUploadedFile(f"testfile_{x}.png", b"file_content"),
                original_file_name=f"testfile_{x}.png",
            )
        form = forms.UploadDocumentsForm(
            files={
                "file": [
                    good_file,
                ]
            },
            request=request_object,
            licence_object=licence,
        )
        assert not form.is_valid()
        assert "file" in form.errors
        assert form.errors.as_data()["file"][0].code == "too_many"

    def test_invalid_extension_file_name_escaped(self, request_object):
        bad_file = SimpleUploadedFile("<img src=xonerror=alert(document.domain)>gif.gif", b"GIF8")
        bad_file.original_name = "<img src=xonerror=alert(document.domain)>gif.gif"

        form = forms.UploadDocumentsForm(
            files={
                "file": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "file" in form.errors
        assert (
            form.errors.as_data()["file"][0].message
            == "<img src=xonerror=alert(document.domain)>gif.gif cannot be uploaded.\n\nThe selected file must be a "
            "DOC, DOCX, ODT, FODT, XLS, XLSX, ODS, FODS, PPT, PPTX, ODP, FODP, PDF, TXT, CSV, "
            "ZIP, HTML, JPEG, JPG or PNG"
        )
