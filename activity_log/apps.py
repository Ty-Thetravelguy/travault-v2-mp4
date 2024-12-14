from django.apps import AppConfig


class ActivityLogConfig(AppConfig):
    """
    Configuration class for the Activity Log application.
    This class is used to configure the application and its settings.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activity_log'