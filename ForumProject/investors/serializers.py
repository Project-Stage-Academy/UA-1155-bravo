from rest_framework import serializers
from .models import Investor


class InvestorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Startup model.

    Attributes:
        id (int): The ID of the startup (read-only).
        startup_name (str): The name of the startup.
        startup_logo (ImageField): The logo of the startup.
        startup_industry (str): The industry of the startup.
        startup_phone (str): The phone number of the startup.
        startup_country (CountryField): The country where the startup is located.
        startup_city (str): The city where the startup is located.
        startup_address (str): The address of the startup.
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
        value = value.strip()
        value = value[0].upper() + value[1:]
        if not value:
            raise serializers.ValidationError("Investor name cannot be empty.")
        if Investor.objects.filter(investor_name=value).exists():
            raise serializers.ValidationError("Startup name must be unique.")
        return value
