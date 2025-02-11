import os

from apply_for_a_licence.fields import MultipleFileField
from apply_for_a_licence.models import Document
from core.document_storage import TemporaryDocumentStorage
from core.forms.base_forms import BaseModelForm
from core.utils import get_mime_type
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout
from django import forms
from django_chunk_upload_handlers.clam_av import VirusFoundInFileException
from utils.s3 import get_all_session_files


class UploadDocumentsForm(BaseModelForm):
    revalidate_on_done = False
    save_and_return = True
    storage = TemporaryDocumentStorage()

    class Meta:
        model = Document
        fields = ["file"]
        widgets = {
            "file": MultipleFileField(),
        }
        labels = {
            "file": "Upload a file",
        }
        help_texts = {"file": "Maximum individual file size 100MB. Maximum number of uploads 10."}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False
        self.fields["file"].widget.attrs["class"] = "govuk-file-upload moj-multi-file-upload__input"
        self.fields["file"].widget.attrs["name"] = "file"
        # redefining this to remove the 'Continue' button from the helper
        self.helper = FormHelper()
        self.helper.layout = Layout("file")

    def clean_file(self) -> list[Document]:
        documents = self.cleaned_data.get("file")
        for document in documents:

            # does the document contain a virus?
            try:
                document.readline()
            except VirusFoundInFileException:
                documents.remove(document)
                raise forms.ValidationError(
                    "The selected file contains a virus",
                )

            # is the document a valid file type?
            mimetype = get_mime_type(document.file)
            valid_mimetype = mimetype in [
                # word documents
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
                # spreadsheets
                "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                # powerpoints
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                # pdf
                "application/pdf",
                # other
                "text/plain",
                "text/csv",
                "application/zip",
                "text/html",
                # images
                "image/jpeg",
                "image/png",
            ]
            valid_extensions = [
                # word documents
                ".doc",
                ".docx",
                ".odt",
                ".fodt",
                # spreadsheets
                ".xls",
                ".xlsx",
                ".ods",
                ".fods",
                # powerpoints
                ".ppt",
                ".pptx",
                ".odp",
                ".fodp",
                # pdf
                ".pdf",
                # other
                ".txt",
                ".csv",
                ".zip",
                ".html",
                # images
                ".jpeg",
                ".jpg",
                ".png",
            ]

            _, file_extension = os.path.splitext(document.name)
            valid_extension = file_extension.lower() in valid_extensions
            valid_file_types = (
                ", ".join(valid_extensions[:-1]).replace(".", "").upper() + " or " + valid_extensions[-1].replace(".", "").upper()
            )

            if not valid_mimetype or not valid_extension:
                raise forms.ValidationError(
                    f"{document.original_name} cannot be uploaded.\n\nThe selected file must be a {valid_file_types}",
                    code="invalid_file_type",
                )

            # has the user already uploaded 10 files?
            # TODO: update session_files
            if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
                if len(session_files) + 1 > 10:
                    raise forms.ValidationError("You can only select up to 10 files at the same time", code="too_many")

            # is the document too large?
            if document.size > 104857600:
                raise forms.ValidationError("The selected file must be smaller than 100 MB", code="too_large")

        return documents
