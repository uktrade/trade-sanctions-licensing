import uuid

from core.models import BaseModel, BaseModelID
from django.contrib.postgres.fields import ArrayField
from django.contrib.sessions.models import Session
from django.db import models
from django_chunk_upload_handlers.clam_av import validate_virus_check_result
from django_countries.fields import CountryField

from . import choices


class Applicant(BaseModelID):
    user_email_address = models.EmailField(
        blank=True,
        null=True,
    )
    user_email_verification = models.OneToOneField("UserEmailVerification", on_delete=models.CASCADE, blank=False)
    full_name = models.CharField(max_length=255)
    business = models.CharField(max_length=300, verbose_name="Business you work for", blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    type_of_relationship = models.CharField(
        choices=choices.TypeOfRelationshipChoices.choices,
        max_length=20,
        blank=False,
    )
    held_existing_licence = models.CharField(
        choices=choices.YesNoChoices.choices,
        max_length=11,
        blank=False,
    )
    existing_licences = models.TextField(null=True, blank=True)


class UserEmailVerification(BaseModelID):
    user_session = models.ForeignKey(Session, on_delete=models.CASCADE)
    email_verification_code = models.CharField(max_length=6)
    date_created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)


class Organisation(BaseModel):
    licence = models.ForeignKey("Licence", on_delete=models.CASCADE, blank=False)
    # two name fields required for the case of recipients
    name = models.CharField()
    website = models.URLField(null=True, blank=True)
    do_you_know_the_registered_company_number = models.CharField(
        choices=choices.YesNoChoices.choices,
        max_length=3,
        blank=False,
        null=True,
    )
    registered_company_number = models.CharField(max_length=15, blank=True, null=True)
    registered_office_address = models.CharField(null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    additional_contact_details = models.CharField(blank=True, null=True)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    address_line_3 = models.CharField(max_length=200, blank=True, null=True)
    address_line_4 = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank_label="Select Country", blank=True, null=True)
    town_or_city = models.CharField(max_length=250, blank=True, null=True)
    county = models.CharField(max_length=250, null=True, blank=True)
    type_of_relationship = models.CharField(
        # only allow recipient, business, or named individuals employment details in this table
        # the slice [0:3] specifically excludes the "sole individual"
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


class Individual(BaseModel):
    licence = models.ForeignKey("Licence", on_delete=models.CASCADE, blank=False)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    nationality_and_location = models.CharField(choices=choices.NationalityAndLocation.choices)
    additional_contact_details = models.CharField(blank=True, null=True)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    address_line_3 = models.CharField(max_length=200, blank=True, null=True)
    address_line_4 = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank_label="Select Country", blank=True, null=True)
    town_or_city = models.CharField(max_length=250, blank=True, null=True)
    county = models.CharField(max_length=250, null=True, blank=True)
    relationship_provider = models.TextField(
        blank=True, null=True, db_comment="what is the relationship between the provider and the recipient?"
    )


class Licence(BaseModel):
    applicant = models.OneToOneField("Applicant", on_delete=models.CASCADE, primary_key=True)
    ground = models.ForeignKey("Ground", on_delete=models.CASCADE, blank=True, null=True)
    regimes = ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True)
    reference = models.CharField(max_length=6)
    business_registered_on_companies_house = models.CharField(
        choices=choices.YesNoDoNotKnowChoices.choices,
        max_length=11,
        blank=False,
    )
    services = models.ForeignKey("Services", models.SET_NULL, null=True)
    description_provision = models.TextField(blank=True, null=True)
    purpose_of_provision = models.TextField(blank=True, null=True)

    def assign_reference(self) -> str:
        """Assigns a unique reference to this Licence object"""
        reference = uuid.uuid4().hex[:6].upper()
        if self.__class__.objects.filter(reference=reference).exists():
            return self.assign_reference()
        self.reference = reference
        self.save()
        return reference


# TODO: Currently not in use
class ApplicationStatus(BaseModel):
    licence = models.OneToOneField("Licence", on_delete=models.CASCADE, blank=False)
    status = models.OneToOneField("Status", models.SET_NULL, null=True)
    end_date = models.DateField(null=True, blank=True)


class ApplicationType(BaseModelID):
    short_label = models.CharField()
    who_do_you_want_the_licence_to_cover = models.CharField(
        max_length=255,
        choices=choices.WhoDoYouWantTheLicenceToCoverChoices.choices,
        blank=False,
        null=False,
    )
    label = models.CharField()
    end_date = models.DateField(blank=True, null=True)


class Document(BaseModel):
    licence = models.ForeignKey("Licence", on_delete=models.CASCADE, blank=False)
    file = models.FileField(
        validators=[
            validate_virus_check_result,
        ],
        null=True,
        blank=True,
    )


class Ground(BaseModelID):
    licensing_grounds = ArrayField(models.CharField(choices=choices.LicensingGroundsChoices.choices))
    label = models.CharField()
    end_date = models.DateField(blank=True, null=True)


class Services(BaseModelID):
    type_of_service = models.CharField(choices=choices.TypeOfServicesChoices.choices)
    professional_or_business_service = models.CharField()
    service_activities = models.TextField()
    label = models.CharField(blank=True, null=True)
    cpc_group = models.CharField(blank=True, null=True)
    cpc_class = models.CharField(blank=True, null=True)
    cpc_subclass = models.CharField(blank=True, null=True)
    sic_code = models.IntegerField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)


class Status(BaseModelID):
    status = models.CharField(null=True)
    end_date = models.DateField()
