# Generated by Django 4.0.3 on 2022-03-17 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_name', models.CharField(help_text='format: required', max_length=255, verbose_name='delivery_name')),
                ('delivery_price', models.IntegerField(error_messages={'name': {'max_length': 'the price must be positive'}}, help_text='format:price Toman', verbose_name='delivery price')),
                ('delivery_method', models.CharField(choices=[('IS', 'In Store'), ('HD', 'Home Delivery'), ('DD', 'Digital Delivery')], help_text='format: required', max_length=255, verbose_name='delivery_method')),
                ('delivery_timeframe', models.CharField(help_text='format: required', max_length=255, verbose_name='delivery timeframe')),
                ('delivery_window', models.CharField(help_text='format: required', max_length=255, verbose_name='delivery window')),
                ('order', models.IntegerField(default=0, help_text='format: required', verbose_name='list order')),
                ('is_active', models.BooleanField(default=True, help_text='in visible?', verbose_name='is_active')),
            ],
            options={
                'verbose_name': 'Delivery Option',
                'verbose_name_plural': 'Delivery Options',
            },
        ),
        migrations.CreateModel(
            name='PaymentSelections',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='format: required', max_length=255, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, help_text='in visible?', verbose_name='is_active')),
            ],
            options={
                'verbose_name': 'Payment Selection',
                'verbose_name_plural': 'Payment Selections',
            },
        ),
    ]
