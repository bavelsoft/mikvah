# Generated by Django 4.0.6 on 2023-01-20 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mikvah', '0002_appointment_minutes_offset'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='textable',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
