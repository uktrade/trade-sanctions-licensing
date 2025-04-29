from apply_for_a_licence.tasklist.sub_tasks import PreviousLicensesHeldSubTask
from django.urls import reverse


class TestPreviousLicensesHeldSubTask:
    def test_subtask_values(self, individual_licence):
        sub_task = PreviousLicensesHeldSubTask(individual_licence)
        assert sub_task.name == "Previous licences"
        assert sub_task.help_text == "Any previous licence numbers"
        assert sub_task.url() == reverse("previous_licence", kwargs={"licence_pk": individual_licence.id})

    def test_subtask_is_completed(self, business_licence):
        sub_task = PreviousLicensesHeldSubTask(business_licence)
        assert not sub_task.is_completed
        business_licence.held_existing_licence = True
        business_licence.save()
        assert sub_task.is_completed
