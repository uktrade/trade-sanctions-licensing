# mypy: disable-error-code="attr-defined,misc"
import datetime
import uuid

from core.document_storage import PermanentDocumentStorage
from core.models import BaseModel
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import QuerySet
from django.forms import model_to_dict
from django.utils import timezone
from django_countries.fields import CountryField
from utils.companies_house import get_formatted_address

from . import choices
from .types import Licensee


class Licence(BaseModel):
    """The chief model for the application for a licence. Represents an application"""

    business_registered_on_companies_house = models.CharField(
        choices=choices.YesNoDoNotKnowChoices.choices,
        max_length=11,
        blank=False,
    )
    licensing_grounds = ArrayField(models.CharField(choices=choices.LicensingGroundsChoices.choices), null=True)
    licensing_grounds_legal_advisory = ArrayField(models.CharField(choices=choices.LicensingGroundsChoices.choices), null=True)
    regimes = ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True)
    reference = models.CharField(max_length=6)
    submitter_reference = models.CharField(max_length=255, blank=True, null=True)
    type_of_service = models.CharField(choices=choices.TypeOfServicesChoices.choices)
    professional_or_business_services = ArrayField(
        models.CharField(choices=choices.ProfessionalOrBusinessServicesChoices.choices), null=True
    )
    service_activities = models.TextField()
    description_provision = models.TextField(blank=True, null=True)
    purpose_of_provision = models.TextField(blank=True, null=True)
    held_existing_licence = models.CharField(
        choices=choices.YesNoChoices.choices,
        blank=False,
        null=True,
    )
    existing_licences = models.TextField(null=True, blank=True)
    is_third_party = models.BooleanField(null=True, blank=False)
    who_do_you_want_the_licence_to_cover = models.CharField(
        max_length=255,
        choices=choices.WhoDoYouWantTheLicenceToCoverChoices.choices,
        blank=False,
        null=False,
    )

    applicant_user_email_address = models.EmailField(
        blank=True,
        null=True,
    )
    applicant_full_name = models.CharField(max_length=255, null=True, blank=False)
    applicant_business = models.CharField(max_length=300, verbose_name="Business you work for", blank=False, null=True)
    applicant_role = models.CharField(max_length=255, blank=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="licence_applications")
    status = models.CharField(max_length=10, choices=choices.StatusChoices.choices, default=choices.StatusChoices.draft)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def assign_reference(self) -> str:
        """Assigns a unique reference to this Licence object"""
        reference = uuid.uuid4().hex[:6].upper()
        if self.__class__.objects.filter(reference=reference).exists():
            return self.assign_reference()
        self.reference = reference
        return reference

    @property
    def recipients(self) -> "QuerySet[Organisation]":
        return self.organisations.filter(type_of_relationship=choices.TypeOfRelationshipChoices.recipient)

    def licensees(self) -> list[Licensee]:
        licensees = []

        if self.who_do_you_want_the_licence_to_cover == choices.WhoDoYouWantTheLicenceToCoverChoices.business:
            for organisation in self.organisations.filter(type_of_relationship=choices.TypeOfRelationshipChoices.business):
                licensees.append(
                    Licensee(
                        name=organisation.name,
                        address=organisation.registered_office_address,
                        label_name="Business",
                    )
                )
        elif self.who_do_you_want_the_licence_to_cover in [
            choices.WhoDoYouWantTheLicenceToCoverChoices.individual,
            choices.WhoDoYouWantTheLicenceToCoverChoices.myself,
        ]:
            for individual in self.individuals.all():
                licensees.append(
                    Licensee(
                        name=individual.full_name,
                        address=get_formatted_address(model_to_dict(individual)),
                        label_name="Individual",
                    )
                )

        return licensees

    def get_licensing_grounds_display(self) -> list[str]:
        if self.licensing_grounds:
            return [choices.LicensingGroundsChoices[value].label for value in self.licensing_grounds]
        else:
            return []

    def get_licensing_grounds_legal_advisory_display(self) -> list[str]:
        if self.licensing_grounds_legal_advisory:
            return [choices.LicensingGroundsChoices[value].label for value in self.licensing_grounds_legal_advisory]
        else:
            return []

    def get_professional_or_business_services_display(self) -> list[str]:
        if self.professional_or_business_services:
            return [
                choices.ProfessionalOrBusinessServicesChoices[value].label for value in self.professional_or_business_services
            ]
        else:
            return []

    def get_date_till_deleted(self) -> datetime.datetime:
        return self.created_at + datetime.timedelta(days=settings.DRAFT_APPLICATION_EXPIRY_DAYS)

    def is_expired(self) -> bool:
        """Returns True if the licence has been in draft for more than the set expiry days"""
        if self.status == choices.StatusChoices.draft:
            return timezone.now() > self.get_date_till_deleted()
        else:
            return False


class AddressMixin(models.Model):
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    address_line_3 = models.CharField(max_length=200, blank=True, null=True)
    address_line_4 = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank_label="Select country", blank=True, null=True)
    town_or_city = models.CharField(max_length=250, blank=True, null=True)
    county = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        abstract = True

    def readable_address(self) -> str:
        """Returns a formatted address string for the address fields of this model instance."""
        return get_formatted_address(model_to_dict(self))


class Organisation(BaseModel, AddressMixin):
    licence = models.ForeignKey("Licence", on_delete=models.CASCADE, blank=False, related_name="organisations")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    # two name fields required for the case of recipients
    name = models.CharField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    do_you_know_the_registered_company_number = models.CharField(choices=choices.YesNoChoices.choices, blank=True, null=True)
    business_registered_on_companies_house = models.CharField(
        choices=choices.YesNoDoNotKnowChoices.choices, max_length=11, blank=True, null=True
    )
    registered_company_number = models.CharField(max_length=15, blank=True, null=True)
    registered_office_address = models.CharField(null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    additional_contact_details = models.CharField(blank=True, null=True)
    type_of_relationship = models.CharField(
        # only allow recipient, business, or named individuals employment details in this table
        choices=(
            (choices.TypeOfRelationshipChoices.recipient.value, choices.TypeOfRelationshipChoices.recipient.label),
            (choices.TypeOfRelationshipChoices.business.value, choices.TypeOfRelationshipChoices.business.label),
            (
                choices.TypeOfRelationshipChoices.named_individuals.value,
                choices.TypeOfRelationshipChoices.named_individuals.label,
            ),
        ),
        max_length=20,
        blank=False,
    )
    relationship_provider = models.TextField(
        blank=True, null=True, db_comment="what is the relationship between the provider and the recipient?"
    )

    class Meta:
        ordering = ["created_at"]

    def readable_address(self) -> str:
        """If we have registered_office_address, use that instead of the address fields"""
        if self.registered_office_address:
            return self.registered_office_address
        else:
            return super().readable_address()


class Individual(BaseModel, AddressMixin):
    licence = models.ForeignKey("Licence", on_delete=models.CASCADE, blank=False, related_name="individuals")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    nationality_and_location = models.CharField(choices=choices.NationalityAndLocation.choices)
    additional_contact_details = models.CharField(blank=True, null=True)
    relationship_provider = models.TextField(
        blank=True, null=True, db_comment="what is the relationship between the provider and the recipient?"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Document(BaseModel):
    licence = models.ForeignKey("Licence", on_delete=models.CASCADE, blank=False, related_name="documents")
    file = models.FileField(
        max_length=340,
        null=True,
        blank=True,
        # if we're storing the document in the DB, we can assume it's in the permanent bucket
        storage=PermanentDocumentStorage(),
    )

    def file_name(self) -> str:
        return self.file.name.split("/")[-1]

    def url(self) -> str:
        return self.file.url
