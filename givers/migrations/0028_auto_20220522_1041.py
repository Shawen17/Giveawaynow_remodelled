# Generated by Django 3.1.13 on 2022-05-22 09:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0027_auto_20220522_1025'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ondeliverytransaction',
            old_name='verified',
            new_name='delivered',
        ),
    ]
