from django.db import models
from django.core.exceptions import ValidationError
from .validation import phone_regex, image_validator
from django_countries.fields import CountryField


class Investor(models.Model):
    investor_name = models.CharField(max_length=150)
    investor_logo = models.ImageField(upload_to='media/investor_logos/',
                                      validators=[image_validator], null=True, blank=True)
    investor_industry = models.CharField(max_length=50)
    investor_phone = models.CharField(max_length=20, validators=[phone_regex])
    investor_country = CountryField()
    investor_city = models.CharField(max_length=50)
    investor_address = models.CharField(max_length=150)

    def __str__(self):
        return self.investor_name

    # Validate non-empty startup_name
    def clean(self):
        if (not self.investor_name or not self.investor_industry or not self.investor_phone or not self.investor_city
                or not self.investor_address):
            raise ValidationError("All fields must be filled in: name, industry, phone, country, city, address.")
