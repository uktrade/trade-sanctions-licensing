from apply_for_a_licence.tasklist.base_classes import BaseSubTask, BaseTask


class TestBaseSubTask:
    def test_base_sub_task(self, licence):
        base_subtask = BaseSubTask(licence)
        assert not base_subtask.is_completed
        base_subtask.status = "in_progress"
        assert base_subtask.tag_colour == "light-blue"
        base_subtask.status = "cannot_start"
        assert base_subtask.tag_colour == "blue"


class SubTaskProgress(BaseSubTask):
    name = "Test in progress"

    @property
    def is_in_progress(self):
        return True


class TestBaseTask:
    def test_base_task(self, licence):
        sub_task1 = BaseSubTask
        sub_task2 = SubTaskProgress
        sub_tasks = [sub_task1, sub_task2]
        base_task = BaseTask(licence)
        base_task.sub_tasks = sub_tasks
        assert base_task.get_sub_tasks()[0].status == "not_started"
        assert base_task.get_sub_tasks()[1].status == "in_progress"
