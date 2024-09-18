recipients = {
    "recipient1": {"cleaned_data": {"name": "Recipient 1", "country": "AX", "address_line_1": "AL1", "town_or_city": "Town"}},
    "recipient2": {
        "cleaned_data": {
            "name": "Recipient 2",
            "website": "http://fdas.com",
            "country": "GB",
            "address_line_1": "Line 1",
            "town_or_city": "City",
        }
    },
    "recipient3": {
        "cleaned_data": {"name": "Recipient 3", "address_line_1": "Address 1", "town_or_city": "town3", "country": "NZ"}
    },
}

businesses = {
    "business1": {"cleaned_data": {"name": "Business 1", "country": "AX", "address_line_1": "AL1", "town_or_city": "Town"}},
    "business2": {
        "cleaned_data": {
            "name": "Business 2",
            "website": "http://fdas.com",
            "country": "GB",
            "address_line_1": "Line 1",
            "town_or_city": "City",
        }
    },
    "business3": {
        "cleaned_data": {"name": "Business 3", "address_line_1": "Address 1", "town_or_city": "town3", "country": "NZ"}
    },
}

individuals = {
    "individual1": {
        "name_data": {
            "cleaned_data": {
                "first_name": "Recipient",
                "last_name": "1",
            },
            "dirty_data": {
                "first_name": "Recipient",
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
            },
            "dirty_data": {
                "country": "GB",
                "address_line_1": "AL1",
                "address_line_2": "AL2",
                "county": "Middlesex",
                "town_or_city": "Town",
            },
        },
    },
    "individual2": {
        "name_data": {
            "cleaned_data": {
                "first_name": "Recipient",
                "last_name": "2",
            },
            "dirty_data": {
                "first_name": "Recipient",
                "last_name": "2",
                "nationality_and_location": "uk_national_non_uk_location",
            },
        }
    },
    "individual3": {
        "name_data": {
            "cleaned_data": {"name": "Recipient 3", "address_line_1": "Address 1", "town_or_city": "town3", "country": "NZ"}
        }
    },
}
