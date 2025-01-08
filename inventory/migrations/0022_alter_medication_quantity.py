# Generated by Django 5.1.3 on 2025-01-07 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0021_alter_dispensedmedication_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medication',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
