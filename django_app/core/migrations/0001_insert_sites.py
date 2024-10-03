from django.conf import settings
from django.db import migrations


def insert_sites(apps, schema_editor):
    """Populate the sites model"""
    Site = apps.get_model("sites", "Site")
    Site.objects.all().delete()

    # Register SITE_ID = 1
    Site.objects.create(domain=settings.APPLY_FOR_A_LICENCE_DOMAIN, name="apply-for-a-licence")
    # Register SITE_ID = 2
    Site.objects.create(domain=settings.VIEW_A_LICENCE_DOMAIN, name="view-a-licence")
    if settings.ENVIRONMENT == "production":
        # Register SITE_ID = 3
        Site.objects.create(domain=settings.APPLY_FOR_A_LICENCE_EXTRA_DOMAIN, name="apply-for-a-licence")
        # Register SITE_ID = 4
        Site.objects.create(domain=settings.VIEW_A_LICENCE_EXTRA_DOMAIN, name="view-a-licence")


def remove_sites(apps, schema_editor):
    """Populate the sites model"""
    Site = apps.get_model("sites", "Site")
    Site.objects.all().delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [("sites", "0002_alter_domain_unique")]

    operations = [migrations.RunPython(insert_sites, reverse_code=remove_sites)]
