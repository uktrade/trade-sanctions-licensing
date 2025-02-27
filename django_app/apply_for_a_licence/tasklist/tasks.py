from apply_for_a_licence.tasklist.base_classes import BaseTask
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


class AboutYouTask(BaseTask):
    name = "About you"

    def get_sub_tasks(self):
        sub_tasks = [YourDetailsSubTask(licence=self.licence)]
        if self.licence.who_do_you_want_the_licence_to_cover == "myself":
            sub_tasks.append(PreviousLicensesHeldSubTask(licence=self.licence))
        return sub_tasks


class WhoTheLicenceCoversTask(BaseTask):
    name = "Who the licence covers"

    def get_sub_tasks(self):
        sub_tasks = [
            DetailsOfTheEntityYouWantToCoverSubTask(licence=self.licence),
            PreviousLicensesHeldSubTask(licence=self.licence),
        ]
        return sub_tasks


class AboutTheServicesTask(BaseTask):
    name = "About the services"

    def get_sub_tasks(self):
        sub_tasks = [
            ServicesYouWantToProvideSubTask(licence=self.licence),
            PurposeForProvidingServicesSubTask(licence=self.licence),
        ]
        return sub_tasks


class RecipientsTask(BaseTask):
    name = "Recipients of the services"

    def get_sub_tasks(self):
        sub_tasks = [
            RecipientContactDetailsSubTask(licence=self.licence),
        ]
        return sub_tasks


class ReviewAndSubmitTask(BaseTask):
    name = "Review and submit"

    def get_sub_tasks(self):
        sub_tasks = [CheckYourAnswersSubTask(licence=self.licence)]
        return sub_tasks


class UploadDocumentsTask(BaseTask):
    name = "Upload documents"

    def get_sub_tasks(self):
        sub_tasks = [UploadDocumentsSubTask(licence=self.licence)]
        return sub_tasks
