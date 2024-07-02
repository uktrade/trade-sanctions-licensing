# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Address(models.Model):
    id = models.IntegerField(primary_key=True)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    address_line_3 = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=20)
    country = models.CharField()
    city = models.CharField(max_length=250)
    start_date = models.DateField()
    end_date = models.DateField()
    organisation = models.ForeignKey("Organisation", models.DO_NOTHING, blank=True, null=True)
    applicant = models.ForeignKey("Applicant", models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "address"
        db_table_comment = "The address has a start and end date.  the constraint manages those. "
        "However, it is important for analytical purposes across DBT. "
        "Otherwise, it is unknown when companies had changed their addresses. It helps inferring the source of truth."


class Applicant(models.Model):
    id = models.IntegerField(primary_key=True)
    third_party_flag = models.BooleanField()
    email_address = models.CharField()
    emailed_verified_flag = models.BooleanField()
    full_name = models.CharField()
    phone_number = models.CharField()
    business = models.CharField(blank=True, null=True)
    role = models.CharField(blank=True, null=True)
    uk_national_flag = models.BooleanField()
    dual_national_flag = models.BooleanField()

    class Meta:
        managed = False
        db_table = "applicant"
        db_table_comment = "This table stores data about the applicant and about the verification of emails. "
        "It is to be noted it may need extended at a later stage if a login is required. "


class ApplicationApplicant(models.Model):
    applicant = models.OneToOneField(
        Applicant, models.DO_NOTHING, primary_key=True
    )  # The composite primary key (applicant_id, application_id) found, that is not supported. The first column is selected.
    application = models.ForeignKey("BaseApplication", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "application_applicant"
        unique_together = (("applicant", "application"),)


class ApplicationOrganisation(models.Model):
    application_id = models.IntegerField(
        primary_key=True
    )  # The composite primary key (application_id, organisation_id, start_date) found, that is not supported.
    # The first column is selected.
    organisation_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    recipient_flag = models.BooleanField()
    trader_flag = models.BooleanField()
    relationship = models.CharField(
        blank=True, null=True, db_comment="what is the relationship between the provider and the recipient?"
    )

    class Meta:
        managed = False
        db_table = "application_organisation"
        unique_together = (("application_id", "organisation_id", "start_date"),)


class ApplicationRussianSanction(models.Model):
    application = models.ForeignKey("BaseApplication", models.DO_NOTHING)
    prohibition = models.TextField(db_comment="how do your [services] fall under the definition of prohibited [legislation]?")

    class Meta:
        managed = False
        db_table = "application_russian_sanction"


class ApplicationServices(models.Model):
    application = models.OneToOneField(
        "BaseApplication", models.DO_NOTHING, primary_key=True
    )  # The composite primary key (application_id, services_id) found, that is not supported. The first column is selected.
    services = models.ForeignKey("Services", models.DO_NOTHING)
    direct_flag = models.BooleanField()
    unknown_flag = models.BooleanField()
    description_provision = models.TextField(blank=True, null=True)
    purpose_of_provision = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "application_services"
        unique_together = (("application", "services"),)


class ApplicationStatus(models.Model):
    application = models.OneToOneField(
        "BaseApplication", models.DO_NOTHING, primary_key=True
    )  # The composite primary key (application_id, status_id, start_date) found,
    # that is not supported. The first column is selected.
    status = models.ForeignKey("Status", models.DO_NOTHING)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        managed = False
        db_table = "application_status"
        unique_together = (("application", "status", "start_date"),)
        db_table_comment = "This table can be used to compute the number of days each application is in a certain status. "
        "It can be used for measuring the performance of a trade-sanctions licencing services."


class ApplicationType(models.Model):
    id = models.IntegerField(primary_key=True)
    short_label = models.CharField()
    label = models.CharField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "application_type"
        db_table_comment = "This table is similar to the report_type in Rab. It helps with the first screen to support choice of "
        "type of licences.  The start and end date is important. It supports data analysis and it is automatically generated.  "
        "Some maintenance tasks will be to change the end date and the interaction should be updated.   "


class BaseApplication(models.Model):
    id = models.IntegerField(primary_key=True)
    creation_date = models.DateField()
    regime = models.ForeignKey("Regime", models.DO_NOTHING)
    type_id = models.IntegerField()
    unique_ref = models.CharField(
        db_comment="This reference may need to match a wider data standard as applied in SIELS. I.E. "
        "GB[TYPE OF LICENCE]/[YEAR]/XXXXXXX/[length]\n\n"
        "Type of licence: i.e., SIEL, OEIL, F680. It needs to be defined.\nYear : 2024 ....\nXXXXXXX : 0000001 - "
        " then increment from the start of the calendar year. \n\nlength; "
        "it is permanent (P) or temporary (T).  It is surmised it is T. \n"
    )
    uk_recipient_flag = models.BooleanField()
    ground = models.ForeignKey("Ground", models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "base_application"


class Document(models.Model):
    application_id = models.IntegerField(
        primary_key=True
    )  # The composite primary key (application_id, ref, creation_time) found,
    # that is not supported. The first column is selected.
    ref = models.IntegerField()
    creation_time = models.DateField()
    path = models.CharField()

    class Meta:
        managed = False
        db_table = "document"
        unique_together = (("application_id", "ref", "creation_time"),)
        db_table_comment = "this table is similar as report of breach."


class ExistingLicences(models.Model):
    id = models.IntegerField(
        primary_key=True
    )  # The composite primary key (id, application_id) found, that is not supported. The first column is selected.
    application = models.ForeignKey(BaseApplication, models.DO_NOTHING)
    licence = models.TextField()

    class Meta:
        managed = False
        db_table = "existing_licences"
        unique_together = (("id", "application"),)
        db_table_comment = (
            "Previous licences held by the applicant. " "The first interaction is a text box to capture more than one licence. "
        )
        "However, some other versions include a licence for a text box. "
        "So, we have a one-to-many relationship to support both options. "
        "Also, it is better modelled to prevent empty fields. "


class Ground(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        managed = False
        db_table = "ground"


class Industry(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        managed = False
        db_table = "industry"
        db_table_comment = "This table is new. It is not yet in RaB."


class IndustryRegime(models.Model):
    regime_id = models.IntegerField(
        primary_key=True
    )  # The composite primary key (regime_id, industry_id) found, that is not supported. The first column is selected.
    industry_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = "industry_regime"
        unique_together = (("regime_id", "industry_id"),)


class Organisation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField()
    website = models.CharField()
    registration_number = models.CharField(max_length=15, blank=True, null=True)
    uk_flag = models.BooleanField(db_comment="the company is located in the UK")
    contact_number = models.CharField(blank=True, null=True)
    email = models.CharField(blank=True, null=True)
    additional_contact_details = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "organisation"
        db_table_comment = "This table has been inspired from LITE data model. "
        "If you feel you can use again the model from RaB, then fine. However, this one may be better suited for licences"


class Regime(models.Model):
    id = models.IntegerField(primary_key=True)
    short_name = models.CharField()
    full_name = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()
    shown_gui_flag = models.BooleanField()
    licences_guid_flag = models.BooleanField()

    class Meta:
        managed = False
        db_table = "regime"
        db_table_comment = "this table is similar as RaB. Licensing_gui_flag has been added. "
        "Not all the regimes shown in RaB are shown for trade sanctions licenses. "
        "Also the start and end date brings some flexibility as legislation changes fast. "


class Services(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField(blank=True, null=True)
    cpc_group = models.CharField(blank=True, null=True)
    cpc_class = models.CharField(blank=True, null=True)
    cpc_subclass = models.CharField(blank=True, null=True)
    sic_code = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    industry_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = "services"
        db_table_comment = "This table is not in RaB. It is part of professions."


class Status(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        managed = False
        db_table = "status"
