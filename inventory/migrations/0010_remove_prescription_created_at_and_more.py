# Generated by Django 5.1.3 on 2024-12-29 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_prescription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prescription',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='date',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='doctor',
        ),
        migrations.AddField(
            model_name='prescription',
            name='doctor_name',
            field=models.CharField(default='Sanmitra Aiholli', max_length=255),
        ),
        migrations.AddField(
            model_name='prescription',
            name='dosages',
            field=models.JSONField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='prescription',
            name='follow_up_date',
            field=models.DateField(default=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='prescription',
            name='medications',
            field=models.JSONField(),
        ),
    ]
