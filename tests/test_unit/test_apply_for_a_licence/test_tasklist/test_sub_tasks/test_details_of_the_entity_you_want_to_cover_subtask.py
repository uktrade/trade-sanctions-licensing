from apply_for_a_licence import choices
from apply_for_a_licence.tasklist.sub_tasks import (
    DetailsOfTheEntityYouWantToCoverSubTask,
)
from django.urls import reverse

from tests.factories import IndividualFactory, OrganisationFactory


class TestDetailsOfTheEntityYouWantToCoverSubTask:
    def test_subtask_name(self, individual_licence, business_licence):
        # individual licence
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(individual_licence)
        assert sub_task.name == "Details of the individual you want to cover"
        # business licence
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(business_licence)
        assert sub_task.name == "Details of the business you want to cover"

    def test_subtask_help_text(self, individual_licence, business_licence):
        # individual licence
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(individual_licence)
        assert sub_task.help_text == "Name, address, business they work for"
        # business licence
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(business_licence)
        assert sub_task.help_text == "Name and address of business"

    def test_subtask_url_business(self, business_licence):
        # no previous business
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(business_licence)
        assert (
            sub_task.url
            == reverse("is_the_business_registered_with_companies_house", kwargs={"licence_pk": business_licence.id}) + "?new=yes"
        )
        # previous business in draft state
        organisation = OrganisationFactory(
            licence=business_licence, status="draft", type_of_relationship=choices.TypeOfRelationshipChoices.business
        )
        assert (
            sub_task.url
            == reverse("is_the_business_registered_with_companies_house", kwargs={"licence_pk": business_licence.id})
            + f"?business_id={organisation.id}"
        )
        # completed business
        organisation.status = "complete"
        organisation.save()
        assert sub_task.url == reverse("business_added", kwargs={"licence_pk": business_licence.id})

    def test_subtask_url_individual(self, individual_licence):
        # no previous individual
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(individual_licence)
        assert sub_task.url == reverse("add_an_individual", kwargs={"licence_pk": individual_licence.id}) + "?new=yes"
        # previous individual in draft state
        individual = IndividualFactory(licence=individual_licence, status="draft")
        assert (
            sub_task.url
            == reverse("add_an_individual", kwargs={"licence_pk": individual_licence.id}) + f"?individual_id={individual.id}"
        )
        # completed individual
        individual.status = "complete"
        individual.save()
        assert sub_task.url == reverse("individual_added", kwargs={"licence_pk": individual_licence.id})

    def test_is_completed_business(self, business_licence):
        # no previous business
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(business_licence)
        assert not sub_task.is_completed

    def test_is_completed_individual(self, individual_licence):
        # no previous individual
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(individual_licence)
        assert not sub_task.is_completed

    def test_is_myself_licence(self, yourself_licence):
        sub_task = DetailsOfTheEntityYouWantToCoverSubTask(yourself_licence)
        assert not sub_task.is_completed
        assert not sub_task.is_in_progress
