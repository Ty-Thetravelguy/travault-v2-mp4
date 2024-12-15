from django.apps import AppConfig


class HomeConfig(AppConfig):
    """
    Django app configuration for the Home application.
    
    This class configures the Home app settings including the default
    auto field type and application name.
    """
    # Specifies the type of auto-field to use for primary keys
    default_auto_field = 'django.db.models.BigAutoField'
    # The name of the Django application
    name = 'home'
