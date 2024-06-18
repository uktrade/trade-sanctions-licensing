from .base import *  # noqa

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = True

BASE_FRONTEND_TESTING_URL = "http://apply-for-a-licence:8000"

ENVIRONMENT = "test"

# we don't want to connect to ClamAV in testing, redefine and remove from list
FILE_UPLOAD_HANDLERS = ("core.custom_upload_handler.CustomFileUploadHandler",)  # Order is important
