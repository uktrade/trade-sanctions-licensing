import random
import string

import factory
from apply_for_a_licence.models import Individual, Licence, Organisation
from django.contrib.auth.models import User
from factory.fuzzy import FuzzyText
from feedback.models import FeedbackItem


class ModelFieldLazyChoice(factory.LazyFunction):
    def __init__(self, model_class, field, *args, **kwargs):
        field = model_class._meta.get_field(field)
        choices = [choice[0] for choice in field.choices]
        super().__init__(function=lambda: random.choice(choices), *args, **kwargs)


class ArrayFieldLazyChoice(factory.LazyFunction):
    def __init__(self, model_class, field, *args, **kwargs):
        field = model_class._meta.get_field(field)

        choices = [choice[0] for choice in field.base_field.choices]
        super().__init__(function=lambda: random.choices(choices, k=random.randint(1, len(choices))), *args, **kwargs)


class LicenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Licence

    licensing_grounds = ArrayFieldLazyChoice(Licence, "licensing_grounds")
    business_registered_on_companies_house = ModelFieldLazyChoice(Licence, "business_registered_on_companies_house")
    type_of_service = ModelFieldLazyChoice(Licence, "type_of_service")
    service_activities = factory.Faker("text")
    description_provision = factory.Faker("text")
    purpose_of_provision = factory.Faker("text")
    existing_licences = factory.Faker("text")
    held_existing_licence = ModelFieldLazyChoice(Licence, "held_existing_licence")
    who_do_you_want_the_licence_to_cover = ModelFieldLazyChoice(Licence, "who_do_you_want_the_licence_to_cover")
    is_third_party = factory.Faker("boolean")
    applicant_user_email_address = factory.Faker("email")
    applicant_full_name = factory.Faker("name")
    applicant_business = factory.Faker("company")
    applicant_role = factory.Faker("job")
    reference = FuzzyText(length=4, chars=string.ascii_uppercase + string.digits)


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organisation

    name = factory.Faker("company")
    website = factory.Faker("url")
    registered_company_number = factory.Faker("random_int", min=11111111, max=99999999)
    do_you_know_the_registered_company_number = ModelFieldLazyChoice(Organisation, "do_you_know_the_registered_company_number")
    registered_office_address = factory.Faker("address")
    email = factory.Faker("email")
    type_of_relationship = ModelFieldLazyChoice(Organisation, "type_of_relationship")
    relationship_provider = factory.Faker("text")
    where_is_the_address = ModelFieldLazyChoice(Organisation, "where_is_the_address")


class IndividualFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Individual

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    nationality_and_location = ModelFieldLazyChoice(Individual, "nationality_and_location")
    address_line_1 = factory.Faker("street_address")
    address_line_2 = factory.Faker("secondary_address")
    town_or_city = factory.Faker("city")
    county = factory.Faker("state")
    postcode = factory.Faker("postcode")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    is_active = factory.Faker("boolean")
    is_staff = factory.Faker("boolean")


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeedbackItem

    rating = ModelFieldLazyChoice(FeedbackItem, "rating")
    did_you_experience_any_issues = ArrayFieldLazyChoice(FeedbackItem, "did_you_experience_any_issues")
    how_we_could_improve_the_service = factory.Faker("text")
