# Generated by Django 5.1.3 on 2025-01-05 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_billing'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='billing',
            name='date_billed',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
