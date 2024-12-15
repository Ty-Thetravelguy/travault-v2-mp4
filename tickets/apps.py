from django.apps import AppConfig


class TicketsConfig(AppConfig):
    """
    Django app configuration for the Tickets application.
    
    This class configures the Tickets app settings and ensures proper signal registration
    for ticket-related events.

    Attributes:
        default_auto_field (str): Specifies BigAutoField for primary keys
        name (str): The name identifier for this Django application
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        """
        Performs initialization tasks when the app is ready.
        
        Imports the tickets signals module to ensure all signal handlers
        are properly registered with Django's signal dispatcher.
        """
        import tickets.signals 