import pytest

from tests.factories import IndividualFactory


@pytest.mark.django_db
class TestIndividualModel:
    def test_full_name(self, licence):
        individual = IndividualFactory(licence=licence)
        assert individual.full_name == f"{individual.first_name} {individual.last_name}"
