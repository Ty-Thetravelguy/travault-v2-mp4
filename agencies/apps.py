# agencies/apps.py

from django.apps import AppConfig

class AgenciesConfig(AppConfig):
    """
    Configuration class for the Agencies application.
    This class is used to configure the application and its settings.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agencies' 
    label = 'agencies'