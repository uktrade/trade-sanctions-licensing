# Generated by Django 4.2.15 on 2024-08-22 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0002_alter_historicalorganisation_do_you_know_the_registered_company_number_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalservices",
            name="type_of_service",
            field=models.CharField(
                choices=[
                    ("professional_and_business", "Professional and business services (Russia)"),
                    ("energy_related", "Energy-related services (Russia)"),
                    (
                        "infrastructure_and_tourism_related",
                        "Infrastructure and tourism-related services to non-government controlled Ukrainian territories (Russia)",
                    ),
                    (
                        "interception_or_monitoring",
                        "Interception or monitoring services (Russia, Belarus, Iran, Myanmar, Syria and Venezuela)",
                    ),
                    (
                        "mining_manufacturing_or_computer",
                        "Mining manufacturing or computer services (Democratic People's Republic of Korea",
                    ),
                    ("ships_or_aircraft_related", "Ships or aircraft-related services (Democratic People's Republic of Korea)"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="services",
            name="type_of_service",
            field=models.CharField(
                choices=[
                    ("professional_and_business", "Professional and business services (Russia)"),
                    ("energy_related", "Energy-related services (Russia)"),
                    (
                        "infrastructure_and_tourism_related",
                        "Infrastructure and tourism-related services to non-government controlled Ukrainian territories (Russia)",
                    ),
                    (
                        "interception_or_monitoring",
                        "Interception or monitoring services (Russia, Belarus, Iran, Myanmar, Syria and Venezuela)",
                    ),
                    (
                        "mining_manufacturing_or_computer",
                        "Mining manufacturing or computer services (Democratic People's Republic of Korea",
                    ),
                    ("ships_or_aircraft_related", "Ships or aircraft-related services (Democratic People's Republic of Korea)"),
                ]
            ),
        ),
    ]