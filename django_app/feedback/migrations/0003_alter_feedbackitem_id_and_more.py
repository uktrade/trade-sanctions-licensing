# Generated by Django 4.2.13 on 2024-07-09 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0002_remove_feedbackitem_did_you_experience_any_issues_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedbackitem",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="historicalfeedbackitem",
            name="id",
            field=models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID"),
        ),
    ]
