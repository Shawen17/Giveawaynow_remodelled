# Generated by Django 3.1.13 on 2022-05-27 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0031_auto_20220527_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='give',
            name='address',
            field=models.TextField(default='Head office'),
        ),
    ]
