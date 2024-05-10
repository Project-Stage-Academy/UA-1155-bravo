from rest_framework import serializers
from .models import Startup
from django.core.exceptions import ValidationError
import re

class StartupSerializer(serializers.ModelSerializer):
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
        model = Startup
        fields = [
            'id',
            'startup_name',
            'startup_logo',
            'startup_industry',
            'startup_phone',
            'startup_country',
            'startup_city',
            'startup_address'
        ]
        read_only_fields = ['id']

