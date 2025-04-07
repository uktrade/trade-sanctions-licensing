from apply_for_a_licence.tasklist import Tasklist
from apply_for_a_licence.tasklist.sub_tasks import (
    CheckYourAnswersSubTask,
    DetailsOfTheEntityYouWantToCoverSubTask,
    PreviousLicensesHeldSubTask,
    PurposeForProvidingServicesSubTask,
    RecipientContactDetailsSubTask,
    ServicesYouWantToProvideSubTask,
    UploadDocumentsSubTask,
    YourDetailsSubTask,
)
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


class TestTaskListSubTasks:
    def test_aboutyou_subtasks(self, individual_licence, yourself_licence):
        # individual licence
        tasklist = Tasklist(individual_licence).get_tasks()
        assert tasklist[0].name == "About you"
        assert isinstance(tasklist[0], AboutYouTask)
        assert len(tasklist[0].sub_tasks) == 1
        assert isinstance(tasklist[0].sub_tasks[0](individual_licence), YourDetailsSubTask)
        # myself licence
        tasklist = Tasklist(yourself_licence).get_tasks()
        assert tasklist[0].name == "About you"
        assert len(tasklist[0].sub_tasks) == 2
        assert isinstance(tasklist[0].sub_tasks[0](yourself_licence), YourDetailsSubTask)
        assert isinstance(tasklist[0].sub_tasks[1](yourself_licence), PreviousLicensesHeldSubTask)

    def test_whothelicencecovers_subtasks(self, individual_licence, business_licence):
        # individual licence
        tasklist = Tasklist(individual_licence).get_tasks()
        assert tasklist[1].name == "Who the licence covers"
        assert isinstance(tasklist[1], WhoTheLicenceCoversTask)
        assert len(tasklist[1].sub_tasks) == 2
        assert isinstance(tasklist[1].sub_tasks[0](individual_licence), DetailsOfTheEntityYouWantToCoverSubTask)
        assert isinstance(tasklist[1].sub_tasks[1](individual_licence), PreviousLicensesHeldSubTask)
        # business licence
        tasklist = Tasklist(business_licence).get_tasks()
        assert tasklist[1].name == "Who the licence covers"
        assert isinstance(tasklist[1], WhoTheLicenceCoversTask)
        assert len(tasklist[1].sub_tasks) == 2
        assert isinstance(tasklist[1].sub_tasks[0](business_licence), DetailsOfTheEntityYouWantToCoverSubTask)
        assert isinstance(tasklist[1].sub_tasks[1](business_licence), PreviousLicensesHeldSubTask)

    def test_abouttheservices_subtasks(self, individual_licence, business_licence, yourself_licence):
        # individual licence
        tasklist = Tasklist(individual_licence).get_tasks()
        assert tasklist[2].name == "About the services"
        assert isinstance(tasklist[2], AboutTheServicesTask)
        assert len(tasklist[2].sub_tasks) == 2
        assert isinstance(tasklist[2].sub_tasks[0](individual_licence), ServicesYouWantToProvideSubTask)
        assert isinstance(tasklist[2].sub_tasks[1](individual_licence), PurposeForProvidingServicesSubTask)
        # business licence
        tasklist = Tasklist(business_licence).get_tasks()
        assert tasklist[2].name == "About the services"
        assert isinstance(tasklist[2], AboutTheServicesTask)
        assert len(tasklist[2].sub_tasks) == 2
        assert isinstance(tasklist[2].sub_tasks[0](business_licence), ServicesYouWantToProvideSubTask)
        assert isinstance(tasklist[2].sub_tasks[1](business_licence), PurposeForProvidingServicesSubTask)
        # myself licence
        tasklist = Tasklist(yourself_licence).get_tasks()
        assert tasklist[1].name == "About the services"
        assert isinstance(tasklist[1], AboutTheServicesTask)
        assert len(tasklist[1].sub_tasks) == 2
        assert isinstance(tasklist[1].sub_tasks[0](yourself_licence), ServicesYouWantToProvideSubTask)
        assert isinstance(tasklist[1].sub_tasks[1](yourself_licence), PurposeForProvidingServicesSubTask)

    def test_recipients_subtasks(self, individual_licence, business_licence, yourself_licence):
        # individual licence
        tasklist = Tasklist(individual_licence).get_tasks()
        assert tasklist[3].name == "Recipients of the services"
        assert isinstance(tasklist[3], RecipientsTask)
        assert len(tasklist[3].sub_tasks) == 1
        assert isinstance(tasklist[3].sub_tasks[0](individual_licence), RecipientContactDetailsSubTask)
        # business licence
        tasklist = Tasklist(business_licence).get_tasks()
        assert tasklist[3].name == "Recipients of the services"
        assert isinstance(tasklist[3], RecipientsTask)
        assert len(tasklist[3].sub_tasks) == 1
        assert isinstance(tasklist[3].sub_tasks[0](business_licence), RecipientContactDetailsSubTask)
        # myself licence
        tasklist = Tasklist(yourself_licence).get_tasks()
        assert tasklist[2].name == "Recipients of the services"
        assert isinstance(tasklist[2], RecipientsTask)
        assert len(tasklist[2].sub_tasks) == 1
        assert isinstance(tasklist[2].sub_tasks[0](yourself_licence), RecipientContactDetailsSubTask)

    def test_uploaddocuments_subtasks(self, individual_licence, business_licence, yourself_licence):
        # individual licence
        tasklist = Tasklist(individual_licence).get_tasks()
        assert tasklist[4].name == "Upload documents"
        assert tasklist[4].is_task_complete
        assert isinstance(tasklist[4], UploadDocumentsTask)
        assert len(tasklist[4].sub_tasks) == 1
        assert isinstance(tasklist[4].sub_tasks[0](individual_licence), UploadDocumentsSubTask)
        # business licence
        tasklist = Tasklist(business_licence).get_tasks()
        assert tasklist[4].name == "Upload documents"
        assert tasklist[4].is_task_complete
        assert isinstance(tasklist[4], UploadDocumentsTask)
        assert len(tasklist[4].sub_tasks) == 1
        assert isinstance(tasklist[4].sub_tasks[0](business_licence), UploadDocumentsSubTask)
        # myself licence
        tasklist = Tasklist(yourself_licence).get_tasks()
        assert tasklist[3].name == "Upload documents"
        assert tasklist[3].is_task_complete
        assert isinstance(tasklist[3], UploadDocumentsTask)
        assert len(tasklist[3].sub_tasks) == 1
        assert isinstance(tasklist[3].sub_tasks[0](yourself_licence), UploadDocumentsSubTask)

    def test_reviewandsubmit_subtasks(self, individual_licence, business_licence, yourself_licence):
        # individual licence
        tasklist = Tasklist(individual_licence).get_tasks()
        assert tasklist[5].name == "Review and submit"
        assert isinstance(tasklist[5], ReviewAndSubmitTask)
        assert len(tasklist[5].sub_tasks) == 1
        assert isinstance(tasklist[5].sub_tasks[0](individual_licence), CheckYourAnswersSubTask)
        # business licence
        tasklist = Tasklist(business_licence).get_tasks()
        assert tasklist[5].name == "Review and submit"
        assert isinstance(tasklist[5], ReviewAndSubmitTask)
        assert len(tasklist[5].sub_tasks) == 1
        assert isinstance(tasklist[5].sub_tasks[0](business_licence), CheckYourAnswersSubTask)
        # myself licence
        tasklist = Tasklist(yourself_licence).get_tasks()
        assert tasklist[4].name == "Review and submit"
        assert isinstance(tasklist[4], ReviewAndSubmitTask)
        assert len(tasklist[4].sub_tasks) == 1
        assert isinstance(tasklist[4].sub_tasks[0](yourself_licence), CheckYourAnswersSubTask)
