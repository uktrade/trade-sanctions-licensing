from apply_for_a_licence.tasklist import Tasklist
from apply_for_a_licence.tasklist.tasks import (
    AboutTheServicesTask,
    AboutYouTask,
    RecipientsTask,
    ReviewAndSubmitTask,
    UploadDocumentsTask,
    WhoTheLicenceCoversTask,
)


class TestTaskList:
    def test_tasklist_tasks_individual(self, individual_licence):
        tasklist = Tasklist(individual_licence).get_tasks()
        assert len(tasklist) == 6
        assert isinstance(tasklist[0], AboutYouTask)
        assert isinstance(tasklist[1], WhoTheLicenceCoversTask)
        assert isinstance(tasklist[2], AboutTheServicesTask)
        assert isinstance(tasklist[3], RecipientsTask)
        assert isinstance(tasklist[4], UploadDocumentsTask)
        assert isinstance(tasklist[5], ReviewAndSubmitTask)

    def test_tasklist_tasks_business(self, business_licence):
        tasklist = Tasklist(business_licence).get_tasks()
        assert len(tasklist) == 6
        assert isinstance(tasklist[0], AboutYouTask)
        assert isinstance(tasklist[1], WhoTheLicenceCoversTask)
        assert isinstance(tasklist[2], AboutTheServicesTask)
        assert isinstance(tasklist[3], RecipientsTask)
        assert isinstance(tasklist[4], UploadDocumentsTask)
        assert isinstance(tasklist[5], ReviewAndSubmitTask)

    def test_tasklist_tasks_myself(self, yourself_licence):
        tasklist = Tasklist(yourself_licence).get_tasks()
        assert len(tasklist) == 5
        assert isinstance(tasklist[0], AboutYouTask)
        assert isinstance(tasklist[1], AboutTheServicesTask)
        assert isinstance(tasklist[2], RecipientsTask)
        assert isinstance(tasklist[3], UploadDocumentsTask)
        assert isinstance(tasklist[4], ReviewAndSubmitTask)
