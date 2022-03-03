# Generated by Django 4.0.2 on 2022-03-02 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_product_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='units_sold',
            field=models.IntegerField(default=0, help_text='format: required, default-0', verbose_name='units sold to date'),
        ),
    ]