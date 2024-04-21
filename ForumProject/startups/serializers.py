from rest_framework import serializers
from .models import Startup

class StartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = [
            'id',
            'startup_name',
            # 'startup_logo',
            'startup_industry',
            'startup_phone',
            'startup_country',
            'startup_city',
            'startup_address'
        ]

    # Validation for startup_name non-empty and uniqueness
    def validate_startup_name(self, value):
        value = value.strip()
        value = value[0].upper() + value[1:]
        if not value:
            raise serializers.ValidationError("Startup name cannot be empty.")
        if Startup.objects.filter(startup_name=value).exists():
            raise serializers.ValidationError("Startup name must be unique.")
        return value
