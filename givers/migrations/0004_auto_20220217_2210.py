# Generated by Django 3.1.13 on 2022-02-17 21:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0003_auto_20220217_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickupcentre',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='city', to='givers.state'),
        ),
    ]