from django import forms
from django.core.files.uploadedfile import UploadedFile


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.__class__.__name__ = "ClearableFileInput"


class MultipleFileField(forms.FileField):
    def __init__(self, *args: object, **kwargs: object) -> None:
        kwargs.setdefault(
            "widget", MultipleFileInput(attrs={"class": "govuk-file-upload moj-multi-file-upload__input", "name": "file"})
        )
        super().__init__(*args, **kwargs)

    def clean(self, data: list[UploadedFile], initial: UploadedFile | None = None) -> list[UploadedFile] | UploadedFile:
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
