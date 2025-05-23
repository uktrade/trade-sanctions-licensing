import base64
from typing import Any

import requests
from apply_for_a_licence.exceptions import (
    CompaniesHouse500Error,
    CompaniesHouseException,
)
from django.conf import settings
from django_countries import countries

COMPANIES_HOUSE_BASE_DOMAIN = "https://api.companieshouse.gov.uk"


def get_companies_house_basic_auth_token(api_key: str = settings.COMPANIES_HOUSE_API_KEY) -> str:
    """
    Returns the basic auth token for Companies House API.
    """
    return base64.b64encode(bytes(f"{api_key}:", "utf-8")).decode("utf-8")


def get_details_from_companies_house(registration_number: str) -> dict[str, Any]:
    """
    Retrieves and returns details of a company from Companies House
    using registration number that is passed in.
    """

    get_company_headers = {"Authorization": f"Basic {get_companies_house_basic_auth_token()}"}
    response = requests.get(
        f"{COMPANIES_HOUSE_BASE_DOMAIN}/company/{registration_number}",
        headers=get_company_headers,
    )
    if response.status_code == 200:
        return response.json()

    if response.status_code == 500:
        raise CompaniesHouse500Error

    raise CompaniesHouseException(f"Companies House API request failed: {response.status_code}")


def get_formatted_address(address_dict: dict[str, Any]) -> str:
    """Get formatted, human-readable address from Companies House address dict."""
    address_string = ""

    if line_1 := address_dict.get("address_line_1"):
        address_string += line_1

    if line_2 := address_dict.get("address_line_2"):
        address_string += f",\n {line_2}"

    if town_or_city := address_dict.get("town_or_city"):
        address_string += f",\n {town_or_city}"
    if postcode := address_dict.get("postcode"):
        address_string += f",\n {postcode}"
    # Companies House address formats
    if locality := address_dict.get("locality"):
        address_string += f",\n {locality}"
    if postal_code := address_dict.get("postal_code"):
        address_string += f" \n {postal_code}"

    if country := address_dict.get("country"):
        if country in ["England", "Northern Ireland", "Scotland", "Wales", "United Kingdom", "England/Wales"]:
            # companies house API returns the full country name, so we just normalise it here to United Kingdom
            address_string += ",\n United Kingdom"
        else:
            COUNTRY_DICT = dict(countries)
            address_string += f",\n {COUNTRY_DICT[country]}"

    return address_string
