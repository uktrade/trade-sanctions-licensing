import pytest

from tests.factories import OrganisationFactory


@pytest.mark.django_db
class TestIndividualModel:
    def test_readable_address(self, licence):
        organisation = OrganisationFactory(
            licence=licence,
            address_line_1="address_line_1",
            address_line_2="address_line_2",
            address_line_3="address_line_3",
            address_line_4="address_line_4",
            postcode="postcode",
            country="GB",
            town_or_city="town_or_city",
            registered_office_address="",
        )
        assert organisation.readable_address() == "address_line_1,\n address_line_2,\n town_or_city,\n postcode"

        # now if we provide a registered_office_address it should pull from there
        organisation = OrganisationFactory(
            licence=licence,
            address_line_1="address_line_1",
            address_line_2="address_line_2",
            address_line_3="address_line_3",
            address_line_4="address_line_4",
            postcode="postcode",
            country="GB",
            town_or_city="town_or_city",
            registered_office_address="registered office address",
        )
        assert organisation.readable_address() == "registered office address"
