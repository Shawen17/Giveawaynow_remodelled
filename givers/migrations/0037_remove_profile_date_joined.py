# Generated by Django 3.1.13 on 2022-06-13 18:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0036_auto_20220613_1951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='date_joined',
        ),
    ]