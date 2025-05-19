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

        for task in tasks:
            if task.name == "Upload documents":
                continue
            else:
                if not task.is_task_complete():
                    tasks.append(ReviewAndSubmitTask(licence=self.licence, can_go_to_cya=False))
                    return tasks

        tasks.append(ReviewAndSubmitTask(licence=self.licence, can_go_to_cya=True))
        return tasks
