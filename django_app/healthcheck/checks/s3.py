from botocore.exceptions import EndpointConnectionError
from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage


def s3_check() -> bool:
    """
    Performs a basic check on the S3 connection
    """
    temporary_document_bucket = TemporaryDocumentStorage().connection.head_bucket(
        Bucket=TemporaryDocumentStorage.bucket_name,
    )
    permanent_document_bucket = PermanentDocumentStorage().bucket
    try:
        assert temporary_document_bucket.head
        assert permanent_document_bucket.creation_date
        return True
    except EndpointConnectionError:
        return False
