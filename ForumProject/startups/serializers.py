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
