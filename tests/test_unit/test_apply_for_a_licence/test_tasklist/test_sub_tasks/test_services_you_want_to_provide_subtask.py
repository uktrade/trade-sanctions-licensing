from apply_for_a_licence.tasklist.sub_tasks import ServicesYouWantToProvideSubTask
from django.urls import reverse


class TestServicesYouWantToProvideSubTask:
    def test_subtask_values(self, individual_licence):
        sub_task = ServicesYouWantToProvideSubTask(individual_licence)
        assert sub_task.name == "The services you want to provide"
        assert sub_task.help_text == "Description of your services"
        assert sub_task.url() == reverse("type_of_service", kwargs={"licence_pk": individual_licence.id})

    def test_subtask_is_completed(self, business_licence):
        sub_task = ServicesYouWantToProvideSubTask(business_licence)
        assert not sub_task.is_completed
        business_licence.service_activities = ["text"]
        business_licence.save()
        assert sub_task.is_completed

    def test_subtask_is_in_progress(self, yourself_licence):
        sub_task = ServicesYouWantToProvideSubTask(yourself_licence)
        assert not sub_task.is_in_progress
        yourself_licence.type_of_service = "text"
        yourself_licence.save()
        assert sub_task.is_in_progress
        assert not sub_task.is_completed
