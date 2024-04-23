from django.apps import AppConfig


class StartupsConfig(AppConfig):
    """
    Configuration class for the 'startups' app.

    Attributes:
        default_auto_field (str): The default auto field to use for models in this app.
        name (str): The name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'startups'
