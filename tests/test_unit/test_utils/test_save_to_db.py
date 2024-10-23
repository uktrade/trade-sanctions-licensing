import pytest
from apply_for_a_licence.models import (
    Individual,
    Organisation,
    Session,
    UserEmailVerification,
)
from utils.save_to_db import SaveToDB

from tests.test_unit.test_utils import data


@pytest.mark.django_db
def test_save_basic_licence(request_object):

    user_email_address = "test@testmail.com"
    request_object.session["user_email_address"] = user_email_address
    request_object.session.save()
    verify_code = "012345"
    user_session = Session.objects.get(session_key=request_object.session.session_key)
    UserEmailVerification.objects.create(
        user_session=user_session,
        email_verification_code=verify_code,
        verified=True,
    )

    save_object = SaveToDB(
        request_object,
        data=data.cleaned_data,
        is_individual=False,
        is_on_companies_house=False,
        is_third_party=False,
    )
    licence = save_object.save_licence()
    assert licence.is_third_party is False
    assert licence.applicant_role == data.cleaned_data["your_details"]["applicant_role"]
    assert licence.existing_licences == data.cleaned_data["previous_licence"]["existing_licences"]
    assert licence.held_existing_licence == data.cleaned_data["previous_licence"]["held_existing_licence"]


@pytest.mark.django_db
def test_save_individuals(request_object):
    user_email_address = "test@testmail.com"
    request_object.session["user_email_address"] = user_email_address
    request_object.session.save()
    verify_code = "012345"
    user_session = Session.objects.get(session_key=request_object.session.session_key)
    UserEmailVerification.objects.create(
        user_session=user_session,
        email_verification_code=verify_code,
        verified=True,
    )

    request_object.session["individuals"] = data.individuals
    save_object = SaveToDB(
        request_object,
        data=data.cleaned_data,
        is_individual=False,
        is_on_companies_house=False,
        is_third_party=False,
    )
    save_object.save_licence()
    save_object.save_individuals()
    licence_individuals = Individual.objects.filter(licence=save_object.licence_object.id)
    assert save_object.licence_object.individuals.count() == 3
    assert licence_individuals[0].last_name == "1"
    assert licence_individuals[0].nationality_and_location == "uk_national_uk_location"
    assert licence_individuals[1].last_name == "2"
    assert licence_individuals[1].nationality_and_location == "uk_national_non_uk_location"
    assert licence_individuals[2].last_name == "3"
    assert licence_individuals[2].nationality_and_location == "non_uk_national_uk_location"


@pytest.mark.django_db
def test_save_myself(request_object):
    user_email_address = "test@testmail.com"
    request_object.session["user_email_address"] = user_email_address
    request_object.session.save()
    verify_code = "012345"
    user_session = Session.objects.get(session_key=request_object.session.session_key)
    UserEmailVerification.objects.create(
        user_session=user_session,
        email_verification_code=verify_code,
        verified=True,
    )

    request_object.session["individuals"] = data.individuals
    cleaned_data_myself = data.cleaned_data
    cleaned_data_myself["start"]["who_do_you_want_the_licence_to_cover"] = "myself"
    cleaned_data_myself["add_yourself"]["first_name"] = "Jane"
    cleaned_data_myself["add_yourself"]["last_name"] = "Doe"
    cleaned_data_myself["add_yourself"]["nationality_and_location"] = "uk_national_uk_location"
    cleaned_data_myself["add_yourself_address"]["address_line_1"] = "Myself Address"
    cleaned_data_myself["add_yourself_address"]["postcode"] = "MM1 1MM"
    cleaned_data_myself["add_yourself_address"]["country"] = "GB"

    save_object = SaveToDB(
        request_object,
        data=cleaned_data_myself,
        is_individual=False,
        is_on_companies_house=False,
        is_third_party=False,
    )
    save_object.save_licence()
    save_object.save_individuals()
    licence_individuals = Individual.objects.filter(licence=save_object.licence_object.id)
    assert save_object.licence_object.applicant_full_name == "Jane Doe"
    assert save_object.licence_object.individuals.count() == 4
    assert licence_individuals[0].last_name == "1"
    assert licence_individuals[0].nationality_and_location == "uk_national_uk_location"
    assert licence_individuals[1].last_name == "2"
    assert licence_individuals[1].nationality_and_location == "uk_national_non_uk_location"
    assert licence_individuals[2].last_name == "3"
    assert licence_individuals[2].nationality_and_location == "non_uk_national_uk_location"
    assert licence_individuals[3].last_name == "Doe"
    assert licence_individuals[3].address_line_1 == "Myself Address"


@pytest.mark.django_db
def test_save_recipients(request_object):
    user_email_address = "test@testmail.com"
    request_object.session["user_email_address"] = user_email_address
    request_object.session.save()
    verify_code = "012345"
    user_session = Session.objects.get(session_key=request_object.session.session_key)
    UserEmailVerification.objects.create(
        user_session=user_session,
        email_verification_code=verify_code,
        verified=True,
    )

    request_object.session["recipients"] = data.recipients
    save_object = SaveToDB(
        request_object,
        data=data.cleaned_data,
        is_individual=False,
        is_on_companies_house=False,
        is_third_party=False,
    )
    save_object.save_licence()
    save_object.save_recipient()
    licence_recipients = Organisation.objects.filter(licence=save_object.licence_object.id)
    assert save_object.licence_object.recipients.count() == 2
    assert licence_recipients[0].name == "Recipient 1"
    assert licence_recipients[0].relationship_provider == "friends"
    assert licence_recipients[1].name == "Recipient 2"
    assert licence_recipients[1].relationship_provider == "suppliers"
