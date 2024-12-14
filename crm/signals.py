# crm/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from activity_log.models import Meeting, Call, Email
from tickets.models import Ticket
from .models import Company

@receiver([post_save], sender=Meeting)
@receiver([post_save], sender=Call)
@receiver([post_save], sender=Email)
@receiver([post_save], sender=Ticket)
def update_company_last_activity(sender, instance, created, **kwargs):
    """
    Update the last activity date of the associated company when a related activity is created.

    This function listens for post_save signals from Meeting, Call, Email, and Ticket models.
    When a new instance of any of these models is created, it checks if the instance has an
    associated company. If so, it updates the company's last_activity_date to the current time.

    Args:
        sender: The model class that sent the signal.
        instance: The actual instance being saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.
    """
    if created and hasattr(instance, 'company') and instance.company:
        company = instance.company
        company.last_activity_date = timezone.now()
        company.save(update_fields=['last_activity_date'])