# Generated by Django 3.1.13 on 2022-02-21 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0008_auto_20220219_2212'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
