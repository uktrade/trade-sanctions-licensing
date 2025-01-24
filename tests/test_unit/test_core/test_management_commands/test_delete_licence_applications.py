from apply_for_a_licence.models import Licence
from django.core.management import call_command

from tests.factories import LicenceFactory


def test_successful_delete(db):
    LicenceFactory(reference="123")
    LicenceFactory(reference="456")

    assert Licence.objects.count() == 2

    call_command("delete_licence_reports", ["123", "456"])
    assert Licence.objects.count() == 0


def test_doesnt_exist_delete(db):
    LicenceFactory(reference="123")

    assert Licence.objects.count() == 1

    call_command("delete_licence_reports", ["456"])
    assert Licence.objects.count() == 1
