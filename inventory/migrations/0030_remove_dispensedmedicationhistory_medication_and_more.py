# Generated by Django 5.1.3 on 2025-01-09 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0029_remove_dispensedmedication_procedure_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dispensedmedicationhistory',
            name='medication',
        ),
        migrations.RemoveField(
            model_name='dispensedmedicationhistory',
            name='procedureCost',
        ),
        migrations.RemoveField(
            model_name='dispensedmedicationhistory',
            name='quantity',
        ),
        migrations.AddField(
            model_name='dispensedmedicationhistory',
            name='consultation_charge',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dispensedmedicationhistory',
            name='medication_details',
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dispensedmedicationhistory',
            name='procedure_cost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='dispensedmedicationhistory',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='dispensedmedicationhistory',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispensed_histories', to='inventory.patient'),
        ),
    ]
