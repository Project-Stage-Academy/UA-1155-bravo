# Generated by Django 5.0.4 on 2024-04-30 20:03

import django.core.validators
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Startup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startup_name', models.CharField(max_length=150, unique=True)),
                ('startup_industry', models.CharField(max_length=50)),
                ('startup_phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message="The phone number must be in the format: '+1234567890'. The Minimum length 9 Maximum length 15 digits.", regex='^\\+1?\\d{9,15}$')])),
                ('startup_country', django_countries.fields.CountryField(max_length=2)),
                ('startup_city', models.CharField(max_length=50)),
                ('startup_address', models.CharField(max_length=150)),
                ('startup_logo', models.ImageField(blank=True, null=True, upload_to='media/startup_logos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'], message='Only files with extensions: jpg, jpeg, png, gif are allowed.')])),
            ],
        ),
    ]
