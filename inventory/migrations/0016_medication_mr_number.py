# Generated by Django 5.1.3 on 2025-01-02 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_remove_medication_expiry_date_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='mr_number',
            field=models.CharField(default='Unknown', max_length=255),
        ),
    ]
