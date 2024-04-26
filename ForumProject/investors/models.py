from django.db import models
from django.core.exceptions import ValidationError
from .validation import phone_regex, image_validator
from django_countries.fields import CountryField


class Investor(models.Model):
    """
    Represents an investor entity.

    Attributes:
        investor_name (str): The name of the investor.
        investor_logo (File): The logo of the investor.
        investor_industry (str): The industry of the investor.
        investor_phone (str): The phone number of the investor.
        investor_country (CountryField): The country of the investor.
        investor_city (str): The city of the investor.
        investor_address (str): The address of the investor.
    """

    investor_name = models.CharField(max_length=150)
    investor_logo = models.ImageField(upload_to='media/investor_logos/',
                                      validators=[image_validator], null=True, blank=True)
    investor_industry = models.CharField(max_length=50)
    investor_phone = models.CharField(max_length=20, validators=[phone_regex])
    investor_country = CountryField()
    investor_city = models.CharField(max_length=50)
    investor_address = models.CharField(max_length=150)

    def __str__(self):
        """
        Returns a string representation of the investor.

        Returns:
            str: The name of the investor.
        """
        return self.investor_name

    # Validate non-empty startup_name
    def clean(self):
        """
        Validate that all required fields are filled in.

        Raises:
            ValidationError: If any of the required fields are empty.
        """
        if (not self.investor_name or not self.investor_industry or not self.investor_phone or not self.investor_city
                or not self.investor_address):
            raise ValidationError("All fields must be filled in: name, industry, phone, country, city, address.")
