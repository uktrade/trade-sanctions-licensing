from apply_for_a_licence.models import Licence
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Deletes licence applications when given a list of application references. "
        "Usage: pipenv run django_app/python manage.py delete_licence_applications <reference> <reference> ..."
    )

    def add_arguments(self, parser):
        parser.add_argument("licence_references", nargs="+", type=str)

    def handle(self, *args, **options):
        for reference in options["licence_references"]:
            try:
                licence_object = Licence.objects.get(reference=reference)
                licence_object.delete()
            except Licence.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Licence {reference} does not exist"))
                continue

            self.stdout.write(self.style.SUCCESS(f"Successfully deleted Licence application {reference}"))
