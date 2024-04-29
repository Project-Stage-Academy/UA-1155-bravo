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
        
    def validate_investor_name(self, value):
        """
        Validate the investor name for non-empty and uniqueness.

        Parameters:
            value (str): The investor name to validate.

        Returns:
            str: The validated investor name.

        Raises:
            serializers.ValidationError: If the investor name is empty or not unique.
        """

        value = value.strip()
        value = value[0].upper() + value[1:]
        if not value:
            raise serializers.ValidationError("Investor name cannot be empty.")
        if Investor.objects.filter(investor_name=value).exists():

            raise serializers.ValidationError("Investor name must be unique.")
        return value

