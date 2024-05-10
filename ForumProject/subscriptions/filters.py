import django_filters
from .models import SubscribeInvestorStartup
from django_filters import rest_framework as dfilters
from django_countries import countries

class MySubscriptionFilter(django_filters.FilterSet):
    """
    FilterSet for filtering user subscriptions.

    This FilterSet allows filtering user subscriptions based on startup name, industry, and country.

    Attributes:
        startup_name (CharFilter): Filter by startup name, performing case-insensitive containment match.
        startup_industry (CharFilter): Filter by startup industry, performing case-insensitive containment match.
        startup_country (ChoiceFilter): Filter by startup country, using choices from Django Countries.
    """
    startup_name = django_filters.CharFilter(field_name='startup__startup_name', lookup_expr='icontains')
    startup_industry = django_filters.CharFilter(field_name='startup__startup_industry', lookup_expr='icontains')
    startup_country = dfilters.ChoiceFilter(
        label='startup country',
        choices=countries,
        field_name='startup__startup_country'
    )

    class Meta:
        model = SubscribeInvestorStartup
        fields = ['startup_name', 'startup_industry', 'startup_country']
