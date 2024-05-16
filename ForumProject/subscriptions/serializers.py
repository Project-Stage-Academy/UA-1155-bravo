from rest_framework import serializers
from .models import SubscribeInvestorStartup

class SubscribeInvestorStartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribeInvestorStartup
        fields = ['id', 'investor', 'startup', 'saved_at']
        read_only_fields = ['id', 'investor']