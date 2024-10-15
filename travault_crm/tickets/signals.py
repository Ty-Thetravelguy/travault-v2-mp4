# travault_crm/tickets/signals.py

from django.db import models  # Import models to use models.ForeignKey
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict

from .models import Ticket, TicketAction

@receiver(pre_save, sender=Ticket)
def log_ticket_update(sender, instance, **kwargs):
    if not instance.pk:
        # Ticket is being created, not updated
        return

    try:
        old_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        return

    old_values = model_to_dict(old_instance)
    new_values = model_to_dict(instance)

    changes = []
    for field in new_values.keys():
        if field in ['updated_at', 'created_at', 'updated_by']:
            continue
        old_value = old_values.get(field)
        new_value = new_values.get(field)
        if old_value != new_value:
            try:
                field_object = Ticket._meta.get_field(field)

                if isinstance(field_object, models.ForeignKey):
                    old_value_display = str(getattr(old_instance, field)) if getattr(old_instance, field) else 'None'
                    new_value_display = str(getattr(instance, field)) if getattr(instance, field) else 'None'
                elif hasattr(field_object, 'choices') and field_object.choices:
                    old_value_display = dict(field_object.choices).get(old_value, str(old_value))
                    new_value_display = dict(field_object.choices).get(new_value, str(new_value))
                else:
                    old_value_display = str(old_value)
                    new_value_display = str(new_value)

                changes.append(
                    f"{field.replace('_', ' ').capitalize()} changed from '{old_value_display}' to '{new_value_display}'"
                )
            except Exception as e:
                print(f"Error processing field {field}: {str(e)}")

    if changes:
        update_message = "\n".join(changes)
        TicketAction.objects.create(
            ticket=instance,
            action_type='update',
            details=update_message,
            created_by=instance.updated_by,
            is_system_generated=True
        )