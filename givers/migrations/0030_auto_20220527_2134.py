# Generated by Django 3.1.13 on 2022-05-27 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0029_auto_20220523_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='give',
            name='category',
            field=models.CharField(blank=True, choices=[('fun', 'Furniture'), ('clo', 'Clothes'), ('shoe', 'Shoes'), ('toy', 'toys'), ('elect', 'Electronics'), ('bag', 'Bags'), ('phone', 'mobile-phones'), ('lappy', 'Laptops'), ('book', 'Books'), ('kit_util', 'Kitchen-utensils'), ('bic', 'Bicyle'), ('acce', 'Accessories'), ('food_item', 'Food-stuffs'), ('groce', 'Groceries'), ('gen', 'Generator'), ('beau_pro', 'Beauty-product'), ('owanbe', 'Natives')], default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='category',
            field=models.CharField(choices=[('fun', 'Furniture'), ('clo', 'Clothes'), ('shoe', 'Shoes'), ('toy', 'toys'), ('elect', 'Electronics'), ('bag', 'Bags'), ('phone', 'mobile-phones'), ('lappy', 'Laptops'), ('book', 'Books'), ('kit_util', 'Kitchen-utensils'), ('bic', 'Bicyle'), ('acce', 'Accessories'), ('food_item', 'Food-stuffs'), ('groce', 'Groceries'), ('gen', 'Generator'), ('beau_pro', 'Beauty-product'), ('owanbe', 'Natives')], max_length=100),
        ),
    ]
