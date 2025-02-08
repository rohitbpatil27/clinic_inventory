# Generated by Django 4.2.18 on 2025-02-08 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0036_rename_cost_dispensedmedicationhistory_total_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispensedmedicationhistory',
            name='medication_details',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dispensedmedicationhistory',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.patient'),
        ),
        migrations.AlterField(
            model_name='dispensedmedicationhistory',
            name='payment_method',
            field=models.CharField(default='Cash', max_length=10),
        ),
        migrations.AlterField(
            model_name='dispensedmedicationhistory',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
