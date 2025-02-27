from apply_for_a_licence.tasklist.base_classes import BaseSubTask, BaseTask
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

    @property
    def sub_tasks(self):
        sub_tasks = [YourDetailsSubTask]
        if self.licence.who_do_you_want_the_licence_to_cover == "myself":
            sub_tasks.append(PreviousLicensesHeldSubTask)
        return sub_tasks


class WhoTheLicenceCoversTask(BaseTask):
    name = "Who the licence covers"
    sub_tasks = [
        DetailsOfTheEntityYouWantToCoverSubTask,
        PreviousLicensesHeldSubTask,
    ]


class AboutTheServicesTask(BaseTask):
    name = "About the services"
    sub_tasks = [
        ServicesYouWantToProvideSubTask,
        PurposeForProvidingServicesSubTask,
    ]


class RecipientsTask(BaseTask):
    name = "Recipients of the services"
    sub_tasks = [
        RecipientContactDetailsSubTask,
    ]


class ReviewAndSubmitTask(BaseTask):
    name = "Review and submit"
    sub_tasks = [
        CheckYourAnswersSubTask,
    ]

    def __init__(self, can_go_to_cya: bool, *args, **kwargs):
        self.can_go_to_cya = can_go_to_cya
        super().__init__(*args, **kwargs)

    def get_sub_tasks(self) -> list[BaseSubTask]:
        sub_tasks = super().get_sub_tasks()
        for each in sub_tasks:
            if self.can_go_to_cya:
                each.status = "not_started"
            else:
                each.status = "cannot_start"

        return sub_tasks


class UploadDocumentsTask(BaseTask):
    name = "Upload documents"
    sub_tasks = [
        UploadDocumentsSubTask,
    ]
