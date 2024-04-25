from django_filters import rest_framework as dfilters
from .models import Startup
from projects.models import Project
from django_countries import countries



class CharFilterInFilter(dfilters.BaseInFilter, dfilters.CharFilter):
    """
    A custom filter for filtering based on a list of values.

    Inherits:
        dfilters.BaseInFilter: Base class for "in" filters.
        dfilters.CharFilter: CharFilter class for character-based filtering.

    """
    pass


class StartupFilter(dfilters.FilterSet):
    """
    A filter set for filtering startups.

    Inherits:
        dfilters.FilterSet: Base class for filter sets.

    Attributes:
        startup_name (dfilters.CharFilter): Filter for startup name with 'contains' lookup.
        startup_industry (dfilters.CharFilter): Filter for startup industry with 'iexact' lookup.
        startup_country (dfilters.ChoiceFilter): Filter for startup country with choices.
        project_status (dfilters.ChoiceFilter): Filter for project status with choices.

    """
    startup_name = dfilters.CharFilter(lookup_expr='contains')
    startup_industry = dfilters.CharFilter(lookup_expr='iexact')
    startup_country = dfilters.ChoiceFilter(
        label='startup country',
        choices=countries,
    
    )
    project_status = dfilters.ChoiceFilter(
        field_name='projects__project_status',
        label='Investment needs',
        choices=Project.PROJECT_STATUS_CHOICES
    )

    
    class Meta:
        model = Startup
        fields = ['startup_name', 'startup_industry', 'project_status']


