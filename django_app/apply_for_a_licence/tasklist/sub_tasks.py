import uuid

from apply_for_a_licence import choices
from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.models import Individual, Organisation
from apply_for_a_licence.tasklist.base_classes import BaseSubTask
from django.urls import reverse, reverse_lazy


class YourDetailsSubTask(BaseSubTask):
    name = "Your details"

    @property
    def help_text(self):
        if self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.myself:
            return "Your name and address, details of anyone else you want to add"
        else:
            return ""

    @property
    def url(self):
        if self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.myself:
            try:
                applicant_individual = self.licence.individuals.filter(is_applicant=True).get()
                return reverse("add_yourself", kwargs={"yourself_uuid": applicant_individual.pk})
            except Individual.DoesNotExist:
                return reverse("add_yourself", kwargs={"yourself_uuid": uuid.uuid4()})
        else:
            return reverse("are_you_third_party")

    @property
    def is_completed(self):
        if self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.myself:
            return (
                self.licence.individuals.filter(is_applicant=True, status="complete").exists()
                and not self.licence.individuals.filter(is_applicant=False, status="draft").exists()
            )
        else:
            return bool(self.licence.applicant_full_name)

    @property
    def is_in_progress(self):
        if self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.myself:
            return (
                self.licence.individuals.filter(is_applicant=True, status="draft").exists()
                or self.licence.individuals.filter(is_applicant=False, status="draft").exists()
            ) and not self.is_completed
        else:
            return not self.is_completed and self.licence.is_third_party is not None


class DetailsOfTheEntityYouWantToCoverSubTask(BaseSubTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_business = (
            self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.business
        )

    @property
    def name(self) -> str:
        if self.is_business:
            return "Details of the business you want to cover"
        else:
            return "Details of the individual you want to cover"

    @property
    def help_text(self):
        if self.is_business:
            return "Name and address of business"
        else:
            return "Name, address, business they work for"

    @property
    def url(self):
        if self.is_business:
            for obj in Organisation.objects.filter(licence=self.licence):
                if obj.status == "complete":
                    return reverse("business_added")
            else:
                new_business = Organisation.objects.create(
                    licence=self.licence, type_of_relationship=TypeOfRelationshipChoices.business
                )
                return reverse("is_the_business_registered_with_companies_house") + f"business_id={new_business.id}"
        else:
            if self.licence.individuals.filter(is_applicant=False).exists():
                return reverse("individual_added")
            else:
                return reverse("add_an_individual", kwargs={"individual_uuid": str(uuid.uuid4())})

    @property
    def is_completed(self) -> bool:
        if self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.business:
            return (
                self.licence.organisations.filter(
                    type_of_relationship=choices.TypeOfRelationshipChoices.business, status="complete"
                ).exists()
                and not self.licence.organisations.filter(
                    type_of_relationship=choices.TypeOfRelationshipChoices.business, status="draft"
                ).exists()
            )
        elif self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.individual:
            return (
                self.licence.individuals.filter(is_applicant=False, status="complete").exists()
                and self.licence.organisations.filter(
                    type_of_relationship=choices.TypeOfRelationshipChoices.named_individuals, status="complete"
                ).exists()
            ) and not self.licence.individuals.filter(is_applicant=False, status="draft").exists()
        else:
            return False

    @property
    def is_in_progress(self) -> bool:
        if self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.business:
            return (
                self.licence.organisations.filter(
                    type_of_relationship=choices.TypeOfRelationshipChoices.business, status="draft"
                ).exists()
                and not self.is_completed
            )
        elif self.licence.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.individual:
            return self.licence.individuals.filter(is_applicant=False, status="draft").exists() or (
                self.licence.individuals.filter(is_applicant=False, status="complete").exists()
                and not self.licence.organisations.filter(
                    type_of_relationship=choices.TypeOfRelationshipChoices.named_individuals, status="complete"
                ).exists()
            )
        else:
            return False


class PreviousLicensesHeldSubTask(BaseSubTask):
    name = "Previous licences"
    help_text = "Any previous licence numbers"
    url = reverse_lazy("previous_licence")

    @property
    def is_completed(self):
        return bool(self.licence.held_existing_licence)


class ServicesYouWantToProvideSubTask(BaseSubTask):
    name = "The services you want to provide"
    help_text = "Description of your services"
    url = reverse_lazy("type_of_service")

    @property
    def is_completed(self) -> bool:
        return self.licence.service_activities is not None

    @property
    def is_in_progress(self) -> bool:
        return not self.is_completed and self.licence.type_of_service


class PurposeForProvidingServicesSubTask(BaseSubTask):
    name = "Your purpose for providing the services"
    help_text = "Licensing grounds or alignment with sanctions regulations"

    @property
    def is_completed(self):
        return bool(self.licence.purpose_of_provision)

    @property
    def url(self):
        if self.licence.type_of_service == choices.TypeOfServicesChoices.professional_and_business:
            return reverse("licensing_grounds")
        else:
            return reverse("purpose_of_provision")

    @property
    def is_in_progress(self) -> bool:
        if self.licence.type_of_service == choices.TypeOfServicesChoices.professional_and_business:
            return not self.is_completed and self.licence.licensing_grounds
        else:
            return False


class UploadDocumentsSubTask(BaseSubTask):
    name = "Upload documents"
    help_text = "Attach files to support your application"
    url = reverse_lazy("upload_documents")

    @property
    def is_completed(self) -> bool:
        return self.licence.documents.exists()


class RecipientContactDetailsSubTask(BaseSubTask):
    name = "Recipient contact details"

    @property
    def is_completed(self) -> bool:
        return (
            self.licence.recipients.filter(status=choices.EntityStatusChoices.complete).exists()
            and not self.licence.recipients.filter(status="draft").exists()
        )

    @property
    def is_in_progress(self) -> bool:
        return self.licence.recipients.filter(status="draft").exists() and not self.is_completed

    @property
    def url(self) -> str:
        for obj in Organisation.objects.filter(licence=self.licence):
            if obj.type_of_relationship == "recipient" and obj.status == "completed":
                return reverse("recipient_added")
        else:
            new_recipient = Organisation.objects.create(licence=self.licence, type_of_relationship="recipient")
            return reverse("where_is_the_recipient_located", kwargs={"recipient_id": new_recipient.id})


class CheckYourAnswersSubTask(BaseSubTask):
    name = "Check your answers before you submit your application"
    url = reverse_lazy("check_your_answers")

    @property
    def is_completed(self) -> bool:
        return self.licence.status == choices.StatusChoices.submitted
