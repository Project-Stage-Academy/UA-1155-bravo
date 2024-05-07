from rest_framework import serializers
from .models import Investor

from django.core.exceptions import ValidationError
import re


class InvestorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Investor model.

    Attributes:
    id (int): The ID of the investor (read-only).
    investor_name (str): The name of the investor.
    investor_logo (ImageField): The logo of the investor.
    investor_industry (str): The industry of the investor.
    investor_phone (str): The phone number of the investor.
    investor_country (CountryField): The country where the investor is located.
    investor_city (str): The city where the investor is located.
    investor_address (str): The address of the investor.
    """


    class Meta:
        model = Investor
        fields = [
            'id',
            'investor_name',
            'investor_logo',
            'investor_industry',
            'investor_phone',
            'investor_country',
            'investor_city',
            'investor_address'
        ]
        read_only_fields = ['id']

