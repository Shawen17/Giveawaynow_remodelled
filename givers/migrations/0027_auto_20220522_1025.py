# Generated by Django 3.1.13 on 2022-05-22 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0026_auto_20220522_1004'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendor',
            old_name='delivered',
            new_name='treated',
        ),
    ]