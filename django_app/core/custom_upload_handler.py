from django.core.files.uploadedfile import UploadedFile
from django_chunk_upload_handlers.s3 import S3FileUploadHandler


class CustomFileUploadHandler(S3FileUploadHandler):
    def file_complete(self, file_size: int) -> UploadedFile | None:
        self.original_file_name = self.file_name
        return super().file_complete(file_size)
