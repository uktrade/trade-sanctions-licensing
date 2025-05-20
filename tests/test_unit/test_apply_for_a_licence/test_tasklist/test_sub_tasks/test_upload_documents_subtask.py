from apply_for_a_licence.models import Document
from apply_for_a_licence.tasklist.sub_tasks import UploadDocumentsSubTask
from django.urls import reverse


class TestPreviousLicensesHeldSubTask:
    def test_subtask_values(self, individual_licence):
        sub_task = UploadDocumentsSubTask(individual_licence)
        assert sub_task.name == "Upload documents"
        assert sub_task.help_text == "Attach files to support your application"
        assert sub_task.url() == reverse("upload_documents", kwargs={"licence_pk": individual_licence.id})

    def test_subtask_is_completed(self, business_licence):
        sub_task = UploadDocumentsSubTask(business_licence)
        assert not sub_task.is_completed
        Document.objects.create(licence=business_licence, temp_file="test123124234.png", original_file_name="test.png")
        assert sub_task.is_completed

    def test_subtask_is_in_progress(self, business_licence):
        sub_task = UploadDocumentsSubTask(business_licence)
        assert not sub_task.is_completed
        business_licence.submitted_documents_form = True
        assert sub_task.is_in_progress

    def test_subtask_not_in_progress(self, business_licence):
        sub_task = UploadDocumentsSubTask(business_licence)
        assert not sub_task.is_completed
        assert not sub_task.is_in_progress
