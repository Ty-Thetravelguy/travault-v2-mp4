from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """
    Django app configuration for the Dashboard application.
    
    This class configures the Dashboard app settings including the default
    auto field type and application name.
    """
    # Specifies the type of auto-field to use for primary keys
    default_auto_field = 'django.db.models.BigAutoField'
    # The name of the Django application
    name = 'dashboard'