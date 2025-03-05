from typing import Dict

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Create the admin user for View a Suspected Breach"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--emails",
            nargs="*",
            help="list of emails to make admin user",
            default=[],
            type=str,
        )

    def handle(self, *args: object, **options: Dict[str, list[str]]) -> None:
        emails = options["emails"]

        user_objects = User.objects.all()
        for email in emails:
            try:
                internal_user_group = Group.objects.get(name=settings.INTERNAL_USER_GROUP_NAME)
                admin_user_group = Group.objects.create(name=settings.ADMIN_USER_GROUP_NAME)

                existing_user = user_objects.get(email=email)
                existing_user.is_staff = True
                existing_user.is_active = True
                existing_user.groups.add(internal_user_group)
                existing_user.groups.add(admin_user_group)
                existing_user.save()
                self.stdout.write(self.style.SUCCESS("User updated successfully"))

            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR("User does not exist"))
