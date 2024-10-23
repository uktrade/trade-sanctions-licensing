cleaned_data = {
    "start": {"who_do_you_want_the_licence_to_cover": "business"},
    "are_you_third_party": {"are_you_applying_on_behalf_of_someone_else": False},
    "what_is_your_email": {"email": "test@testmail.com"},
    "email_verify": {"email_verification_code": "012345"},
    "request_verify_code": {},
    "your_details": {"applicant_full_name": "John Doe", "applicant_business": "DBT", "applicant_role": "Role"},
    "is_the_business_registered_with_companies_house": {"business_registered_on_companies_house": "no"},
    "do_you_know_the_registered_company_number": {},
    "where_is_the_business_located": {"where_is_the_address": "in-uk"},
    "check_company_details": {},
    "manual_companies_house_input": {},
    "business_added": {"do_you_want_to_add_another_business": False},
    "add_an_individual": {},
    "individual_added": {},
    "business_employing_individual": {},
    "add_yourself": {},
    "add_yourself_address": {},
    "yourself_and_individual_added": {},
    "previous_licence": {"held_existing_licence": "yes", "existing_licences": "Licence numbers"},
    "type_of_service": {"type_of_service": "energy_related"},
    "professional_or_business_services": {},
    "service_activities": {"service_activities": "service activities"},
    "which_sanctions_regime": {},
    "where_is_the_recipient_located": {"where_is_the_address": "outside-uk"},
    "recipient_added": {"do_you_want_to_add_another_recipient": False},
    "relationship_provider_recipient": {"relationship": "relationship"},
    "licensing_grounds": {},
    "licensing_grounds_legal_advisory": {},
    "purpose_of_provision": {"purpose_of_provision": "Purposes"},
    "upload_documents": {"document": []},
    "declaration": {},
}


individuals = {
    "individual1": {
        "name_data": {
            "cleaned_data": {
                "first_name": "individual",
                "last_name": "1",
                "nationality_and_location": "uk_national_uk_location",
            },
        },
        "address_data": {
            "cleaned_data": {
                "country": "GB",
                "address_line_1": "AL1",
                "address_line_2": "AL2",
                "county": "Middlesex",
                "town_or_city": "Town",
                "postcode": "BB2 2BB",
            }
        },
    },
    "individual2": {
        "name_data": {
            "cleaned_data": {
                "first_name": "Individual",
                "last_name": "2",
                "nationality_and_location": "uk_national_non_uk_location",
            },
        },
        "address_data": {
            "cleaned_data": {
                "country": "NL",
                "address_line_1": "AL1",
                "address_line_2": "AL2",
                "town_or_city": "Amsterdam",
            }
        },
    },
    "individual3": {
        "name_data": {
            "cleaned_data": {
                "first_name": "Individual",
                "last_name": "3",
                "nationality_and_location": "non_uk_national_uk_location",
            },
        },
        "address_data": {
            "cleaned_data": {"country": "GB", "address_line_1": "Address 1", "town_or_city": "London", "postcode": "AA1 1AA"}
        },
    },
}

recipients = {
    "recipient1": {
        "cleaned_data": {"name": "Recipient 1", "country": "NZ", "address_line_1": "AL1", "town_or_city": "Town"},
        "relationship": "friends",
    },
    "recipient2": {
        "cleaned_data": {
            "name": "Recipient 2",
            "website": "http://fdas.com",
            "country": "GB",
            "address_line_1": "Line 1",
            "town_or_city": "City",
        },
        "relationship": "suppliers",
    },
}
