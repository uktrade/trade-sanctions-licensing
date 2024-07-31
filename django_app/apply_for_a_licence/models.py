import uuid

from core.models import BaseModel, BaseModelID
from django.contrib.sessions.models import Session
from django.db import models
from django_chunk_upload_handlers.clam_av import validate_virus_check_result
from django_countries.fields import CountryField

from . import choices
from .choices import LicensingGroundsChoices


class Address(BaseModelID):
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    address_line_3 = models.CharField(max_length=200, blank=True, null=True)
    address_line_4 = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank_label="Select Country", blank=True, null=True)
    town_or_city = models.CharField(max_length=250, blank=True, null=True)
    county = models.CharField(max_length=250, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    applicant = models.ForeignKey("Applicant", models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "address"
        db_table_comment = "The address has a start and end date.  the constraint manages those. "
        "However, it is important for analytical purposes across DBT. "
        "Otherwise, it is unknown when companies had changed their addresses. It helps inferring the source of truth."
        abstract = True


class Applicant(BaseModelID):
    user_email_address = models.EmailField(
        blank=True,
        null=True,
    )
    user_email_verification = models.ForeignKey("UserEmailVerification", on_delete=models.CASCADE, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    business = models.CharField(max_length=300, verbose_name="Business you work for", blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    uk_national_flag = models.BooleanField()
    dual_national_flag = models.BooleanField()

    class Meta:
        db_table = "applicant"
        db_table_comment = "This table stores data about the applicant and about the verification of emails. "
        "It is to be noted it may need extended at a later stage if a login is required. "


class UserEmailVerification(BaseModelID):
    user_session = models.ForeignKey(Session, on_delete=models.CASCADE)
    email_verification_code = models.CharField(max_length=6)
    date_created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)


class Organisation(Address):
    # two name fields required for the case of recipients
    name = models.CharField()
    name_of_person = models.CharField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    do_you_know_the_registered_company_number = models.CharField(
        choices=choices.YesNoChoices.choices,
        max_length=3,
        blank=False,
    )
    registered_company_number = models.CharField(max_length=15, blank=True, null=True)
    registered_office_address = models.CharField(null=True, blank=True)
    uk_flag = models.BooleanField(db_comment="the company is located in the UK")
    email = models.EmailField(blank=True, null=True)
    additional_contact_details = models.CharField(blank=True, null=True)

    class Meta:
        db_table = "organisation"
        db_table_comment = "This table has been inspired from LITE data model. "
        "If you feel you can use again the model from RaB, then fine. However, this one may be better suited for licences"


class Individual(BaseModelID):
    first_name = models.TextField(max_length=255)
    last_name = models.TextField(max_length=255)
    nationality_and_location = models.CharField(choices=choices.NationalityAndLocation.choices)


class ApplicationApplicant(BaseModel):
    applicant = models.OneToOneField(
        Applicant, models.CASCADE, primary_key=True
    )  # The composite primary key (applicant_id, application_id) found, that is not supported. The first column is selected.
    application = models.ForeignKey("BaseApplication", models.SET_NULL, null=True)

    class Meta:
        db_table = "application_applicant"
        constraints = [models.UniqueConstraint(fields=["applicant", "application"], name="applicant-application")]


class ApplicationOrganisation(BaseModel):
    application_id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4
    )  # The composite primary key (application_id, organisation_id, start_date) found, that is not supported.
    # The first column is selected.
    organisation_id = models.UUIDField(editable=False, default=uuid.uuid4)
    start_date = models.DateField()
    end_date = models.DateField()
    recipient_flag = models.BooleanField()
    trader_flag = models.BooleanField()
    relationship = models.TextField(
        blank=True, null=True, db_comment="what is the relationship between the provider and the recipient?"
    )

    class Meta:
        db_table = "application_organisation"
        constraints = [
            models.UniqueConstraint(
                fields=["application_id", "organisation_id", "start_date"], name="application-organisation-start-date"
            )
        ]


class ApplicationRussianSanction(BaseModel):
    application = models.ForeignKey("BaseApplication", models.SET_NULL, null=True)
    prohibition = models.TextField(db_comment="how do your [services] fall under the definition of prohibited [legislation]?")

    class Meta:
        db_table = "application_russian_sanction"


class ApplicationServices(BaseModel):
    application = models.OneToOneField(
        "BaseApplication", models.CASCADE, primary_key=True
    )  # The composite primary key (application_id, services_id) found, that is not supported. The first column is selected.
    services = models.ForeignKey("Services", models.SET_NULL, null=True)
    direct_flag = models.BooleanField()
    unknown_flag = models.BooleanField()
    description_provision = models.TextField(blank=True, null=True)
    purpose_of_provision = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "application_services"
        constraints = [models.UniqueConstraint(fields=["application", "services"], name="application-services")]


class ApplicationStatus(BaseModel):
    application = models.OneToOneField(
        "BaseApplication", models.CASCADE, primary_key=True
    )  # The composite primary key (application_id, status_id, start_date) found,
    # that is not supported. The first column is selected.
    status = models.ForeignKey("Status", models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "application_status"
        constraints = [
            models.UniqueConstraint(fields=["application", "status", "start_date"], name="application-status-start-date")
        ]
        db_table_comment = "This table can be used to compute the number of days each application is in a certain status. "
        "It can be used for measuring the performance of a trade-sanctions licencing services."


class ApplicationType(BaseModelID):
    short_label = models.CharField()
    who_do_you_want_the_licence_to_cover = models.CharField(
        max_length=255,
        choices=choices.WhoDoYouWantTheLicenceToCoverChoices.choices,
        blank=True,
        null=True,
    )
    label = models.CharField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "application_type"
        db_table_comment = "This table is similar to the report_type in Rab. It helps with the first screen to support choice of "
        "type of licences.  The start and end date is important. It supports data analysis and it is automatically generated.  "
        "Some maintenance tasks will be to change the end date and the interaction should be updated.   "


class BaseApplication(BaseModelID):
    creation_date = models.DateField()
    regime = models.ForeignKey("Regime", models.SET_NULL, null=True)
    type_id = models.UUIDField(editable=False, default=uuid.uuid4)
    unique_ref = models.CharField(
        db_comment="This reference may need to match a wider data standard as applied in SIELS. I.E. "
        "GB[TYPE OF LICENCE]/[YEAR]/XXXXXXX/[length]\n\n"
        "Type of licence: i.e., SIEL, OEIL, F680. It needs to be defined.\nYear : 2024 ....\nXXXXXXX : 0000001 - "
        " then increment from the start of the calendar year. \n\nlength; "
        "it is permanent (P) or temporary (T).  It is surmised it is T. \n"
    )
    uk_recipient_flag = models.BooleanField()
    ground = models.ForeignKey("Ground", models.SET_NULL, null=True, blank=True)
    business_registered_on_companies_house = models.CharField(
        choices=choices.YesNoDoNotKnowChoices.choices,
        max_length=11,
        blank=False,
    )

    class Meta:
        db_table = "base_application"


class Document(BaseModel):
    application_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    # The composite primary key (application_id, ref, creation_time) found,
    # that is not supported. The first column is selected.
    file = models.FileField(
        validators=[
            validate_virus_check_result,
        ],
        null=True,
        blank=True,
    )
    ref = models.IntegerField()
    creation_time = models.DateField()
    path = models.CharField()

    class Meta:
        db_table = "document"
        constraints = [
            models.UniqueConstraint(fields=["application_id", "ref", "creation_time"], name="application-ref-creation-time")
        ]
        db_table_comment = "this table is similar as report of breach."


class ExistingLicences(BaseModelID):
    # The composite primary key (id, application_id) found, that is not supported. The first column is selected.
    application = models.ForeignKey(BaseApplication, models.SET_NULL, null=True)
    licences = models.TextField(null=True, blank=True)
    held_existing_licence = models.CharField(
        choices=choices.YesNoChoices.choices,
        max_length=11,
        blank=False,
    )

    class Meta:
        db_table = "existing_licences"
        constraints = [models.UniqueConstraint(fields=["id", "application"], name="application-id")]
        db_table_comment = (
            "Previous licences held by the applicant. " "The first interaction is a text box to capture more than one licence. "
        )
        "However, some other versions include a licence for a text box. "
        "So, we have a one-to-many relationship to support both options. "
        "Also, it is better modelled to prevent empty fields. "


class Ground(BaseModelID):
    # ! This table is required as it is for data pipelines - speak with data architect before modifying
    licensing_grounds = models.CharField(choices=LicensingGroundsChoices.choices, null=True, blank=True)
    label = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "ground"


class Industry(BaseModelID):
    label = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "industry"
        db_table_comment = "This table is new. It is not yet in RaB."


class IndustryRegime(BaseModel):
    regime_id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4
    )  # The composite primary key (regime_id, industry_id) found, that is not supported. The first column is selected.
    industry_id = models.UUIDField(editable=False, default=uuid.uuid4)

    class Meta:
        db_table = "industry_regime"
        constraints = [models.UniqueConstraint(fields=["regime_id", "industry_id"], name="regime-id-industry-id")]


class Regime(BaseModelID):
    short_name = models.CharField()
    full_name = models.CharField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    shown_gui_flag = models.BooleanField(null=True, blank=True)
    licences_guid_flag = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = "regime"
        db_table_comment = "this table is similar as RaB. Licensing_gui_flag has been added. "
        "Not all the regimes shown in RaB are shown for trade sanctions licenses. "
        "Also the start and end date brings some flexibility as legislation changes fast. "


class Services(BaseModelID):
    type_of_service = models.CharField(choices=choices.TypeOfServicesChoices.choices)
    professional_or_business_service = models.CharField()
    service_activities = models.TextField()
    label = models.CharField(blank=True, null=True)
    cpc_group = models.CharField(blank=True, null=True)
    cpc_class = models.CharField(blank=True, null=True)
    cpc_subclass = models.CharField(blank=True, null=True)
    sic_code = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    industry_id = models.UUIDField(editable=False, default=uuid.uuid4)

    class Meta:
        db_table = "services"
        db_table_comment = "This table is not in RaB. It is part of professions."


class Status(BaseModelID):
    status = models.CharField(null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "status"
