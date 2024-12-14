# billing/apps.py

from django.apps import AppConfig

class BillingConfig(AppConfig):
    """
    Configuration class for the Billing application.

    This class is used to configure the Billing application within
    the Django project. It sets the default auto field type and the name
    of the application. The ready method is used to import the subscription
    module when the application is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'

    def ready(self):
        import billing.subscription