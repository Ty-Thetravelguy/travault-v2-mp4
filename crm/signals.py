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
    if created and hasattr(instance, 'company') and instance.company:
        company = instance.company
        company.last_activity_date = timezone.now()
        company.save(update_fields=['last_activity_date'])