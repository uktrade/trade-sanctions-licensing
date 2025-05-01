from apply_for_a_licence.tasklist.sub_tasks import CheckYourAnswersSubTask
from django.urls import reverse


class TestCheckYourAnswersSubTask:
    def test_subtask_url(self, business_licence):
        sub_task = CheckYourAnswersSubTask(business_licence)
        assert sub_task.url() == reverse("check_your_answers", kwargs={"licence_pk": business_licence.id})
