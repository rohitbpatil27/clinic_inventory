# Generated by Django 5.1.3 on 2024-12-29 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_prescription_created_at_prescription_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prescription',
            name='created_at',
        ),
    ]
