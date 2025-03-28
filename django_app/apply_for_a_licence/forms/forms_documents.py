import os

from apply_for_a_licence.fields import MultipleFileField, MultipleFileInput
from core.document_storage import TemporaryDocumentStorage
from core.forms.base_forms import BaseForm
from core.utils import get_mime_type
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout
from django import forms
from django_chunk_upload_handlers.clam_av import VirusFoundInFileException
from utils.s3 import get_all_session_files


class UploadDocumentsForm(BaseForm):

    file = MultipleFileField(
        required=False,
        label="Upload a file",
        help_text="Maximum individual file size 100MB. Maximum number of uploads 10.",
        widget=MultipleFileInput(
            attrs={
                "class": "govuk-file-upload moj-multi-file-upload__input",
                "name": "file",
            }
        ),
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        # redefining this to remove the 'Continue' button from the helper
        self.helper = FormHelper()
        self.helper.layout = Layout("file")

    def clean_file(self):
        files = self.cleaned_data["file"]
        for file in files:
            try:
                file.readline()
            except VirusFoundInFileException:
                raise forms.ValidationError(
                    "The selected file contains a virus",
                )

            # is the document a valid file type?
            mimetype = get_mime_type(file.file)
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

            _, file_extension = os.path.splitext(file.name)
            valid_extension = file_extension.lower() in valid_extensions
            valid_file_types = (
                ", ".join(valid_extensions[:-1]).replace(".", "").upper() + " or " + valid_extensions[-1].replace(".", "").upper()
            )

            if not valid_mimetype or not valid_extension:
                raise forms.ValidationError(
                    f"{file.original_name} cannot be uploaded.\n\nThe selected file must be a {valid_file_types}",
                    code="invalid_file_type",
                )

            # has the user already uploaded 10 files?
            if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
                if len(session_files) + 1 > 10:
                    raise forms.ValidationError("You can only select up to 10 files at the same time", code="too_many")

            # is the document too large?
            if file.size > 104857600:
                raise forms.ValidationError("The selected file must be smaller than 100 MB", code="too_large")

        return files
