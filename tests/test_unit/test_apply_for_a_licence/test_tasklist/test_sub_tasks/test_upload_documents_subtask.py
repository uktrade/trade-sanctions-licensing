from apply_for_a_licence.tasklist.sub_tasks import UploadDocumentsSubTask
from django.urls import reverse


class TestPreviousLicensesHeldSubTask:
    def test_subtask_values(self, individual_licence):
        sub_task = UploadDocumentsSubTask(individual_licence)
        assert sub_task.name == "Upload documents"
        assert sub_task.help_text == "Attach files to support your application"
        assert sub_task.url == reverse("upload_documents")

    def test_subtask_is_completed(self, business_licence):
        sub_task = UploadDocumentsSubTask(business_licence)
        assert not sub_task.is_completed
        business_licence.documents = "file.png"
        business_licence.save()
        assert sub_task.is_completed
