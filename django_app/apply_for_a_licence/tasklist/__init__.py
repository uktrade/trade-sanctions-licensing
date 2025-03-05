from .sub_tasks import UploadDocumentsSubTask
from .tasks import (
    AboutTheServicesTask,
    AboutYouTask,
    RecipientsTask,
    ReviewAndSubmitTask,
    UploadDocumentsTask,
    WhoTheLicenceCoversTask,
)


class Tasklist:
    def __init__(self, licence):
        self.licence = licence

    def get_tasks(self):
        tasks = [AboutYouTask(licence=self.licence)]
        if self.licence.who_do_you_want_the_licence_to_cover != "myself":
            tasks.append(WhoTheLicenceCoversTask(licence=self.licence))

        tasks.append(AboutTheServicesTask(licence=self.licence))

        tasks.append(RecipientsTask(licence=self.licence))
        tasks.append(UploadDocumentsTask(licence=self.licence))

        # now we need to get the status of each of the sub-tasks so we can figure out if the user is allowed to start
        # the CYA. Basically they should all be complete apart from UploadDocuments because that is optional.

        # note - this code is messy, hard to understand, and resource-wasteful.
        # Please consider optimising I'm sure it can be done better
        all_sub_tasks = [sub_task for task in tasks for sub_task in task.get_sub_tasks()]
        if all([sub_task.is_completed for sub_task in all_sub_tasks if not isinstance(sub_task, UploadDocumentsSubTask)]):
            can_go_to_cya = True
        else:
            can_go_to_cya = False
        tasks.append(ReviewAndSubmitTask(licence=self.licence, can_go_to_cya=can_go_to_cya))
        return tasks
