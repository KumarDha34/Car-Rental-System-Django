# Generated by Django 5.1.6 on 2025-04-10 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0004_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
