# Generated by Django 5.1.3 on 2025-01-07 23:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_alter_billing_patient_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.patient'),
        ),
        migrations.AlterField(
            model_name='dispensedmedication',
            name='medication',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.medication'),
        ),
        migrations.AlterField(
            model_name='dispensedmedication',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.patient'),
        ),
        migrations.AlterField(
            model_name='dispensinghistory',
            name='medication_details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dispensinghistory',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.patient'),
        ),
        migrations.AlterField(
            model_name='dispensinghistory',
            name='procedure',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='medication',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='patient',
            name='age',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
