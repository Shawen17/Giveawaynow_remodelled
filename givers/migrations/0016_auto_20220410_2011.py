# Generated by Django 3.1.13 on 2022-04-10 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('givers', '0015_auto_20220406_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='give',
            name='category',
            field=models.CharField(blank=True, choices=[('furnitures', 'Furniture'), ('clothes', 'Clothes'), ('shoes', 'Shoes'), ('toys', 'toys'), ('electronics', 'Electronics'), ('bags', 'Bags'), ('mobile', 'mobile-phones'), ('laptops', 'Laptops'), ('books', 'Books'), ('kitchen-utensils', 'Kitchen-utensils'), ('bicycle', 'Bicyle'), ('accessories', 'Accessories'), ('food-stuffs', 'Food-stuffs'), ('groceries', 'Groceries'), ('generators', 'Generator'), ('beauty-products', 'Beauty-product')], default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='category',
            field=models.CharField(choices=[('furnitures', 'Furniture'), ('clothes', 'Clothes'), ('shoes', 'Shoes'), ('toys', 'toys'), ('electronics', 'Electronics'), ('bags', 'Bags'), ('mobile', 'mobile-phones'), ('laptops', 'Laptops'), ('books', 'Books'), ('kitchen-utensils', 'Kitchen-utensils'), ('bicycle', 'Bicyle'), ('accessories', 'Accessories'), ('food-stuffs', 'Food-stuffs'), ('groceries', 'Groceries'), ('generators', 'Generator'), ('beauty-products', 'Beauty-product')], max_length=100),
        ),
    ]
