from apply_for_a_licence.models import Individual
from apply_for_a_licence.tasklist.sub_tasks import YourDetailsSubTask
from django.urls import reverse


class TestYourDetailsSubTasks:
    def test_yourdetails_subtask_helptext(self, individual_licence, yourself_licence):
        # individual licence
        sub_task = YourDetailsSubTask(individual_licence)
        assert sub_task.help_text == ""
        sub_task = YourDetailsSubTask(yourself_licence)
        assert sub_task.help_text == "Your name and address, details of anyone else you want to add"

    def test_yourdetails_subtask_url(self, individual_licence, yourself_licence, yourself):
        # individual licence
        sub_task = YourDetailsSubTask(individual_licence)
        assert sub_task.url == reverse("are_you_third_party")
        # yourself licence with applicant
        sub_task = YourDetailsSubTask(yourself_licence)
        applicant_individual = yourself_licence.individuals.filter(is_applicant=True).get()
        assert sub_task.url == reverse("add_yourself", kwargs={"yourself_id": applicant_individual.id})

    def test_yourdetails_subtask_url_no_yourself(self, yourself_licence):
        # yourself licence no applicant added creates new applicant
        sub_task = YourDetailsSubTask(yourself_licence)
        applicant_individual = yourself_licence.individuals.filter(is_applicant=True)
        assert len(applicant_individual) == 0
        assert "your-name-nationality-location" in sub_task.url
        applicant_individual = yourself_licence.individuals.filter(is_applicant=True)
        assert len(applicant_individual) == 1

    def test_is_completed(self, business_licence):
        sub_task = YourDetailsSubTask(business_licence)
        assert not sub_task.is_completed
        business_licence.applicant_full_name = "test_name"
        business_licence.save()
        assert sub_task.is_completed

    def test_is_completed_yourself(self, yourself_licence, yourself):
        sub_task = YourDetailsSubTask(yourself_licence)
        assert sub_task.is_completed

    def test_is_not_completed_without_yourself_applicant(self, yourself_licence):
        sub_task = YourDetailsSubTask(yourself_licence)
        assert not sub_task.is_completed

    def test_is_not_completed_yourself_with_draft_individual(self, yourself_licence, yourself):
        sub_task = YourDetailsSubTask(yourself_licence)
        assert sub_task.is_completed
        Individual.objects.create(licence=yourself_licence, status="draft")
        assert not sub_task.is_completed
