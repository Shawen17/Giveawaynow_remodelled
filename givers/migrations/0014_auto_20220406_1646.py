# Generated by Django 3.1.13 on 2022-04-06 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0013_auto_20220406_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='ticket',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
