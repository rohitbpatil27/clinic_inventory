# Generated by Django 5.1.3 on 2025-01-08 01:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_dispensedmedication_consultation_charge_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dispensedmedication',
            name='consultation_charge',
        ),
        migrations.RemoveField(
            model_name='dispensedmedication',
            name='procedure',
        ),
        migrations.RemoveField(
            model_name='dispensedmedication',
            name='procedure_cost',
        ),
        migrations.AddField(
            model_name='dispensedmedication',
            name='dispensing_history',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='inventory.dispensinghistory'),
        ),
    ]
