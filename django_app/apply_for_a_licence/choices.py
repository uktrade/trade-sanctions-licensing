from crispy_forms_gds.choices import Choice
from django.db import models

YES_NO_CHOICES = (
    Choice(True, "Yes"),
    Choice(False, "No"),
)


class WhoDoYouWantTheLicenceToCoverChoices(models.TextChoices):
    business = "business", "A business or businesses with a UK nexus"
    individual = "individual", "Named individuals with a UK nexus working for a business with no UK nexus"
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
    mining_manufacturing_or_computer = (
        "mining_manufacturing_or_computer",
        "Mining, manufacturing or computer services (Democratic People’s Republic of Korea)",
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
    it_consultancy_and_design = "it_consultancy_and_design", "IT consultancy and design"
    legal_advisory = "legal_advisory", "Legal advisory"
    public_relations = "public_relations", "Public relations"


class LicensingGroundsChoices(models.TextChoices):
    civil_society = (
        "civil_society",
        "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
    )
    energy = "energy", "Services necessary for ensuring critical energy supply to any country"
    divest = (
        "divest",
        "Services necessary for non-Russian persons to divest from Russia, or to wind down business operations in Russia",
    )
    humanitarian = "humanitarian", "The delivery of humanitarian assistance activity"
    parent_or_subsidiary_company = (
        "parent_or_subsidiary_company",
        "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
    )
    medical_and_pharmaceutical = (
        "medical_and_pharmaceutical",
        "Medical and pharmaceutical purposes for the benefit of the civilian population",
    )
    safety = (
        "safety",
        "Services required to enable activities necessary for the urgent prevention or mitigation of an "
        "event likely to have a serious and significant impact on human health or safety, including the "
        "safety of existing infrastructure, or the environment",
    )
    food = "food", "Services in connection with the production or distribution of food for the benefit of the civilian population"


class TypeOfRelationshipChoices(models.TextChoices):
    recipient = "recipient", "Recipient"
    business = "business", "Business"
    named_individuals = "named_individuals", "Named Individuals"
    sole_individual = "sole_individual", "Sole Individual"
