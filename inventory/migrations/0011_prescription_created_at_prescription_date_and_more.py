# Generated by Django 5.1.3 on 2024-12-29 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_remove_prescription_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='created_at',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='follow_up_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='medications',
            field=models.TextField(),
        ),
    ]
