# Generated by Django 5.1.3 on 2024-12-25 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_patient_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='expiry_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
