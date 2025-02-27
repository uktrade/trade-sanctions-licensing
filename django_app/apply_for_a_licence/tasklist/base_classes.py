from typing import Literal


class BaseTask:
    name: str = ""

    def __init__(self, licence, *args, **kwargs):
        self.licence = licence
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> str:
        return self.name.lower().replace(" ", "-")

    def get_sub_tasks(self):
        raise NotImplementedError()

    def can_start_sub_task(self) -> bool:
        return True


class BaseSubTask:
    name: str = ""
    help_text: str = ""
    status: Literal["cannot_start", "not_started", "in_progress", "complete"] = "cannot_start"
    url: str = ""

    def __init__(self, licence, *args, **kwargs):
        self.licence = licence
        super().__init__(*args, **kwargs)

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

    def get_human_readable_status(self) -> str:
        status_mapping = {
            "cannot_start": "Cannot start yet",
            "not_started": "Not yet started",
            "in_progress": "In progress",
            "complete": "Complete",
        }
        return status_mapping[self.status]
