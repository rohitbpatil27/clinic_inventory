# Generated by Django 5.1.3 on 2024-12-25 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_patient_dispensedmedication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='contact',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
