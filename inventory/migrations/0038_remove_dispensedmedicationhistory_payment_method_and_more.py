# Generated by Django 4.2.18 on 2025-02-08 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0037_alter_dispensedmedicationhistory_medication_details_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dispensedmedicationhistory',
            name='payment_method',
        ),
        migrations.AddField(
            model_name='dispensedmedicationhistory',
            name='cash_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dispensedmedicationhistory',
            name='upi_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
