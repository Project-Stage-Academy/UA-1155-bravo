from rest_framework import serializers
from .models import Startup

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

    def validate_startup_name(self, value):
        """
        Validate the startup name for non-empty and uniqueness.

        Parameters:
            value (str): The startup name to validate.

        Returns:
            str: The validated startup name.

        Raises:
            serializers.ValidationError: If the startup name is empty or not unique.
        """
        value = value.strip()
        value = value[0].upper() + value[1:]
        
        if not value:
            raise serializers.ValidationError("Startup name cannot be empty.")
        
        # If this is a POST request, check uniqueness using exists()
        if not self.instance:
            if Startup.objects.filter(startup_name=value).exists():
                raise serializers.ValidationError("Startup name must be unique.")
        # If this is a PUT request, check uniqueness using exclude() and exists()
        else:
            if Startup.objects.filter(startup_name=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Startup name must be unique.")
        
        return value
    