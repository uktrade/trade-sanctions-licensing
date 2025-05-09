from typing import Any

from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


def get_s3_client_from_storage(s3_storage: S3Boto3Storage) -> Any:
    """Get the S3 client object from the storage object."""
    return s3_storage.bucket.meta.client


def generate_presigned_url(s3_storage: Any, s3_file_object: Any) -> str:
    """Generates a Presigned URL for the s3 object."""

    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)

    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_storage.bucket_name, "Key": s3_file_object},
        HttpMethod="GET",
        ExpiresIn=settings.PRESIGNED_URL_EXPIRY_SECONDS,
    )
    return presigned_url


def store_document_in_permanent_bucket(object_key: str) -> None:
    """Copy a specific document from the temporary storage to the permanent storage on s3."""
    temporary_storage_bucket = TemporaryDocumentStorage()
    permanent_storage_bucket = PermanentDocumentStorage()

    permanent_storage_bucket.bucket.meta.client.copy(
        CopySource={
            "Bucket": settings.TEMPORARY_S3_BUCKET_NAME,
            "Key": object_key,
        },
        Bucket=settings.PERMANENT_S3_BUCKET_NAME,
        Key=object_key,
        SourceClient=temporary_storage_bucket.bucket.meta.client,
    )
