from apply_for_a_licence import choices
from apply_for_a_licence.tasklist.sub_tasks import RecipientContactDetailsSubTask
from django.urls import reverse

from tests.factories import OrganisationFactory


class TestRecipientContactDetailsSubTask:
    def test_subtask_name(self, individual_licence):
        # individual licence
        sub_task = RecipientContactDetailsSubTask(individual_licence)
        assert sub_task.name == "Recipient contact details"
        recipient = OrganisationFactory(
            licence=individual_licence, status="draft", type_of_relationship=choices.TypeOfRelationshipChoices.recipient
        )
        assert (
            sub_task.url
            == reverse("where_is_the_recipient_located", kwargs={"licence_pk": individual_licence.id})
            + f"?recipient_id={recipient.id}"
        )
        OrganisationFactory(
            licence=individual_licence, status="complete", type_of_relationship=choices.TypeOfRelationshipChoices.recipient
        )
        assert sub_task.url == reverse("recipient_added", kwargs={"licence_pk": individual_licence.id})
