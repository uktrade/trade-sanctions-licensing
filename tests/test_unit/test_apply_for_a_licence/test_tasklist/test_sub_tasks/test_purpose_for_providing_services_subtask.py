from apply_for_a_licence import choices
from apply_for_a_licence.tasklist.sub_tasks import PurposeForProvidingServicesSubTask
from django.urls import reverse


class TestPurposeForProvidingServicesSubTask:
    def test_subtask_values(self, individual_licence):
        sub_task = PurposeForProvidingServicesSubTask(individual_licence)
        assert sub_task.name == "Your purpose for providing the services"
        assert sub_task.help_text == "Licensing grounds or alignment with sanctions regulations"

    def test_subtask_url(self, business_licence):
        sub_task = PurposeForProvidingServicesSubTask(business_licence)
        assert sub_task.url == reverse("purpose_of_provision")
        business_licence.type_of_service = choices.TypeOfServicesChoices.professional_and_business
        business_licence.save()
        assert sub_task.url == reverse("licensing_grounds")

    def test_subtask_is_completed(self, business_licence):
        sub_task = PurposeForProvidingServicesSubTask(business_licence)
        assert not sub_task.is_completed
        business_licence.purpose_of_provision = "purpose"
        business_licence.save()
        assert sub_task.is_completed

    def test_subtask_is_in_progress(self, yourself_licence):
        sub_task = PurposeForProvidingServicesSubTask(yourself_licence)
        assert not sub_task.is_in_progress
        yourself_licence.type_of_service = choices.TypeOfServicesChoices.professional_and_business
        yourself_licence.save()
        assert not sub_task.is_in_progress
        yourself_licence.licensing_grounds = [choices.LicensingGroundsChoices.food]
        yourself_licence.save()
        assert sub_task.is_in_progress
        assert not sub_task.is_completed
