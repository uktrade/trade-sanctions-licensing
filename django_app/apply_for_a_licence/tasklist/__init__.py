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

        if all([task.is_task_complete() for task in tasks]):
            can_go_to_cya = True
        else:
            can_go_to_cya = False
        tasks.append(ReviewAndSubmitTask(licence=self.licence, can_go_to_cya=can_go_to_cya))
        return tasks
