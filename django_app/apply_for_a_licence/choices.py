from crispy_forms_gds.choices import Choice
from django.db import models

YES_NO_CHOICES = (
    Choice(True, "Yes"),
    Choice(False, "No"),
)


class WhoDoYouWantTheLicenceToCoverChoices(models.TextChoices):
    business = "business", "A business or several businesses"
    individual = "individual", "A named individual or several named individuals"
    myself = "myself", "Myself"


class NationalityAndLocation(models.TextChoices):
    uk_national_uk_location = "uk_national_uk_location", "UK national located in the UK"
    uk_national_non_uk_location = "uk_national_non_uk_location", "UK national located outside the UK"
    dual_national_uk_location = "dual_national_uk_location", "Dual national (includes UK) located in the UK"
    dual_national_non_uk_location = "dual_national_non_uk_location", "Dual national (includes UK) located outside the UK"
    non_uk_national_uk_location = "non_uk_national_uk_location", "Non-UK national located in the UK"


class YesNoChoices(models.TextChoices):
    yes = "yes", "Yes"
    no = "no", "No"


class YesNoDoNotKnowChoices(models.TextChoices):
    yes = "yes", "Yes"
    no = "no", "No"
    do_not_know = "do_not_know", "I do not know"


class TypeOfServicesChoices(models.TextChoices):
    professional_and_business = "professional_and_business", "Professional and business services (Russia)"
    energy_related = "energy_related", "Energy-related services (Russia)"
    infrastructure_and_tourism_related = (
        "infrastructure_and_tourism_related",
        "Infrastructure and tourism-related services to non-government controlled Ukrainian territories (Russia)",
    )
    interception_or_monitoring = (
        "interception_or_monitoring",
        "Interception or monitoring services (Russia, Belarus, Iran, Myanmar, Syria and Venezuela)",
    )
    internet = "internet", "Internet services (Russia and Belarus)"
    mining_manufacturing_or_computer = (
        "mining_manufacturing_or_computer",
        "Mining manufacturing or computer services (Democratic People's Republic of Korea",
    )
    ships_or_aircraft_related = (
        "ships_or_aircraft_related",
        "Ships or aircraft-related services (Democratic People's Republic of Korea)",
    )


class ProfessionalOrBusinessServicesChoices(models.TextChoices):
    accounting = "accounting", "Accounting"
    advertising = "advertising", "Advertising"
    architectural = "architectural", "Architectural"
    auditing = "auditing", "Auditing"
    business_and_management_consulting = "business_and_management_consulting", "Business and management consulting"
    engineering = "engineering", "Engineering"
    it_consultancy_or_design = "it_consultancy_or_design", "IT consultancy or design"
    legal_advisory = "legal_advisory", "Legal advisory"
    public_relations = "public_relations", "Public relations"
