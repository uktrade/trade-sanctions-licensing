from typing import Literal, Type

from apply_for_a_licence.models import Licence


class BaseSubTask:
    name: str = ""
    help_text: str = ""
    status: Literal["cannot_start", "not_started", "in_progress", "complete"] = "cannot_start"
    url: str = ""

    def __init__(self, licence: Licence, *args: object, **kwargs: object) -> None:
        self.licence: Licence = licence
        super().__init__(*args, **kwargs)

    @property
    def is_completed(self) -> bool:
        return False

    @property
    def is_in_progress(self) -> bool:
        return False

    @property
    def tag_colour(self) -> str:
        if self.status == "in_progress":
            return "light-blue"
        elif self.status == "cannot_start":
            return "blue"
        return "blue"

    @property
    def id(self) -> str:
        return self.name.lower().replace(" ", "-")

    @property
    def should_show_tag(self) -> bool:
        return self.status in ["not_started", "in_progress"]

    @property
    def can_start(self) -> bool:
        return self.status in ["not_started", "in_progress", "complete"]

    @property
    def cannot_start(self) -> bool:
        return self.status in ["cannot_start"]

    def get_human_readable_status(self) -> str:
        status_mapping = {
            "cannot_start": "Cannot start yet",
            "not_started": "Not yet started",
            "in_progress": "In progress",
            "complete": "Complete",
        }
        return status_mapping[self.status]


class BaseTask:
    name: str = ""
    sub_tasks: list[Type[BaseSubTask]] = []

    def __init__(self, licence: Licence, *args: object, **kwargs: object) -> None:
        self.licence: Licence = licence
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> str:
        return self.name.lower().replace(" ", "-")

    def get_sub_tasks(self) -> list[BaseSubTask]:
        """Gets an instantiated list of subtasks whilst also setting their status correctly.

        If the previous sub-task has been completed, we can assume the next one is ready to start.
        """
        sub_tasks = [each(self.licence) for each in self.sub_tasks]
        for index, each in enumerate(sub_tasks):
            if each.is_completed:
                each.status = "complete"
                continue

            if each.is_in_progress:
                each.status = "in_progress"
                continue

            if index == 0:
                previous_task_completed = True
            else:
                previous_task_completed = sub_tasks[index - 1].is_completed

            if previous_task_completed:
                each.status = "not_started"
            else:
                each.status = "cannot_start"

        return sub_tasks

    def is_task_complete(self) -> bool:
        """Returns a boolean whether all required subtasks (and therefore the task) has been completed"""
        sub_tasks = self.get_sub_tasks()
        for sub_task in sub_tasks:
            if sub_task.status != "complete":
                return False
        return True
