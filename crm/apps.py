# crm/apps.py

from django.apps import AppConfig

class CrmConfig(AppConfig):
    """
    Configuration class for the CRM application.

    This class is used to configure the CRM application within the Django project.
    It sets the default auto field type and the name of the application. The ready
    method is used to import the necessary modules when the application is ready.

    Attributes:
        default_auto_field (str): The default auto field type for models in this app.
        name (str): The name of the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'

    def ready(self):
        """
        Perform actions when the application is ready.

        This method imports the necessary modules for the CRM application, such as
        template tags and signals, ensuring they are registered and available for use.
        """
        import crm.templatetags.crm_tags
        import crm.signals