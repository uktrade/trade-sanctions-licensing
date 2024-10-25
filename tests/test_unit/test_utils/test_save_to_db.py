from unittest.mock import patch

import pytest
from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.models import (
    Document,
    Individual,
    Organisation,
    Session,
    UserEmailVerification,
)
from utils.save_to_db import SaveToDB

from tests.test_unit.test_utils import data


@pytest.mark.django_db
def save_a_licence(request_object, is_individual, is_on_companies_house, is_third_party, cleaned_data=data.cleaned_data):
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
        data=cleaned_data,
        is_individual=is_individual,
        is_on_companies_house=is_on_companies_house,
        is_third_party=is_third_party,
    )

    return save_object


@pytest.mark.django_db
def test_save_basic_licence(request_object):
    save_object = save_a_licence(request_object, is_individual=False, is_on_companies_house=False, is_third_party=False)
    licence = save_object.save_licence()
    assert licence.is_third_party is False
    assert licence.applicant_role == data.cleaned_data["your_details"]["applicant_role"]
    assert licence.existing_licences == data.cleaned_data["previous_licence"]["existing_licences"]
    assert licence.held_existing_licence == data.cleaned_data["previous_licence"]["held_existing_licence"]


@pytest.mark.django_db
def test_save_individuals(request_object):
    request_object.session["individuals"] = data.individuals
    save_object = save_a_licence(request_object, is_individual=False, is_on_companies_house=False, is_third_party=False)
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
    request_object.session["individuals"] = data.individuals
    cleaned_data_myself = data.cleaned_data
    cleaned_data_myself["start"]["who_do_you_want_the_licence_to_cover"] = "myself"
    cleaned_data_myself["add_yourself"]["first_name"] = "Jane"
    cleaned_data_myself["add_yourself"]["last_name"] = "Doe"
    cleaned_data_myself["add_yourself"]["nationality_and_location"] = "uk_national_uk_location"
    cleaned_data_myself["add_yourself_address"]["address_line_1"] = "Myself Address"
    cleaned_data_myself["add_yourself_address"]["postcode"] = "MM1 1MM"
    cleaned_data_myself["add_yourself_address"]["country"] = "GB"

    save_object = save_a_licence(
        request_object, is_individual=False, is_on_companies_house=False, is_third_party=False, cleaned_data=cleaned_data_myself
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
    request_object.session["recipients"] = data.recipients
    save_object = save_a_licence(request_object, is_individual=False, is_on_companies_house=False, is_third_party=False)
    save_object.save_licence()
    save_object.save_recipient()
    licence_recipients = Organisation.objects.filter(
        licence=save_object.licence_object.id,
        type_of_relationship=TypeOfRelationshipChoices.recipient,
    )
    assert save_object.licence_object.recipients.count() == 2
    assert licence_recipients[0].name == "Recipient 1"
    assert licence_recipients[0].relationship_provider == "friends"
    assert licence_recipients[1].name == "Recipient 2"
    assert licence_recipients[1].relationship_provider == "suppliers"


@pytest.mark.django_db
def test_save_business(request_object):
    request_object.session["businesses"] = data.businesses

    save_object = save_a_licence(request_object, is_individual=False, is_on_companies_house=False, is_third_party=False)
    save_object.save_licence()
    save_object.save_business()
    licence_business = Organisation.objects.filter(
        licence=save_object.licence_object.id,
        type_of_relationship=TypeOfRelationshipChoices.business,
    )
    assert len(licence_business) == 3
    assert licence_business[0].name == "Business 1"
    assert licence_business[0].country == "AX"
    assert licence_business[1].name == "Business 2"
    assert licence_business[1].town_or_city == "City"
    assert licence_business[2].name == "Companies House Business"
    assert licence_business[2].registered_company_number == "12345678"
    assert licence_business[2].registered_office_address == "Address Line 1, GB"


@pytest.mark.django_db
def test_save_business_employing_individual(request_object):

    cleaned_data_business_employing_individual = data.cleaned_data
    cleaned_data_business_employing_individual["business_employing_individual"]["name"] = "John Smith"
    cleaned_data_business_employing_individual["business_employing_individual"]["address_line_1"] = "42 Wallaby Way"
    cleaned_data_business_employing_individual["business_employing_individual"]["country"] = "AU"
    cleaned_data_business_employing_individual["business_employing_individual"]["town_or_city"] = "Sydney"
    save_object = save_a_licence(
        request_object,
        is_individual=True,
        is_on_companies_house=False,
        is_third_party=False,
        cleaned_data=cleaned_data_business_employing_individual,
    )
    save_object.save_licence()
    save_object.save_business()
    licence_business = Organisation.objects.filter(
        licence=save_object.licence_object.id,
        type_of_relationship=TypeOfRelationshipChoices.named_individuals,
    )
    assert len(licence_business) == 1
    assert licence_business[0].name == "John Smith"
    assert licence_business[0].country == "AU"


@patch("utils.save_to_db.store_document_in_permanent_bucket")
@patch("utils.save_to_db.get_all_session_files")
@pytest.mark.django_db
def test_save_document(mocked_get_all_session_files, mocked_store_document_in_permanent_bucket, request_object):
    user_session = Session.objects.get(session_key=request_object.session.session_key)
    save_object = save_a_licence(request_object, is_individual=True, is_on_companies_house=False, is_third_party=False)

    save_object.save_licence()
    mocked_get_all_session_files.return_value = {
        user_session: {
            "file_name": "file.pdf",
            "url": "file_url",
        }
    }
    mocked_store_document_in_permanent_bucket.return_value = "file.pdf"
    save_object.save_documents()
    documents = Document.objects.filter(
        licence=save_object.licence_object.id,
    )

    assert len(documents) == 1
    assert documents[0].file.name == "file.pdf"
    assert "file.pdf" in documents[0].file.url
