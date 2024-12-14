# agent_support/apps.py

from django.apps import AppConfig

class AgentSupportConfig(AppConfig):
    """
    Configuration class for the Agent Support application.

    This class is used to configure the Agent Support application within
    the Django project. It sets the default auto field type and the name
    of the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent_support'