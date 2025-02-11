# Generated by Django 4.2.18 on 2025-01-31 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0018_alter_historicallicence_service_activities_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalorganisation",
            name="business_registered_on_companies_house",
            field=models.CharField(
                choices=[("yes", "Yes"), ("no", "No"), ("do_not_know", "I do not know")], max_length=11, null=True
            ),
        ),
        migrations.AlterField(
            model_name="historicalorganisation",
            name="do_you_know_the_registered_company_number",
            field=models.CharField(choices=[("yes", "Yes"), ("no", "No")], null=True),
        ),
        migrations.AlterField(
            model_name="historicalorganisation",
            name="name",
            field=models.CharField(null=True),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="business_registered_on_companies_house",
            field=models.CharField(
                choices=[("yes", "Yes"), ("no", "No"), ("do_not_know", "I do not know")], max_length=11, null=True
            ),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="do_you_know_the_registered_company_number",
            field=models.CharField(choices=[("yes", "Yes"), ("no", "No")], null=True),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="name",
            field=models.CharField(null=True),
        ),
    ]
