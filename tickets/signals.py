# travault_crm/tickets/signals.py

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict

from .models import Ticket, TicketAction


@receiver(pre_save, sender=Ticket)
def log_ticket_update(sender, instance, **kwargs):
    """
    Signal handler to automatically log changes made to a ticket.
    
    This function captures all changes made to a ticket and creates a TicketAction
    record documenting those changes. It handles different field types appropriately
    (ForeignKey, choice fields, etc.) and formats the changes in a readable format.
    
    Args:
        sender: The model class (Ticket)
        instance: The ticket instance being saved
        kwargs: Additional keyword arguments passed by the signal
    """
    # Skip logging for new ticket creation
    if not instance.pk:
        return

    try:
        # Get the existing ticket instance from the database
        old_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        return

    # Convert instances to dictionaries for comparison
    old_values = model_to_dict(old_instance)
    new_values = model_to_dict(instance)

    # Track all changes made to the ticket
    changes = []
    for field in new_values.keys():
        # Skip timestamp and user tracking fields
        if field in ['updated_at', 'created_at', 'updated_by']:
            continue
            
        old_value = old_values.get(field)
        new_value = new_values.get(field)
        
        # Only process fields that have changed
        if old_value != new_value:
            try:
                field_object = Ticket._meta.get_field(field)

                # Handle different field types appropriately
                if isinstance(field_object, models.ForeignKey):
                    # Format ForeignKey fields
                    old_value_display = str(getattr(old_instance, field)) if getattr(old_instance, field) else 'None'
                    new_value_display = str(getattr(instance, field)) if getattr(instance, field) else 'None'
                elif hasattr(field_object, 'choices') and field_object.choices:
                    # Format choice fields using their display values
                    old_value_display = dict(field_object.choices).get(old_value, str(old_value))
                    new_value_display = dict(field_object.choices).get(new_value, str(new_value))
                else:
                    # Format all other fields as strings
                    old_value_display = str(old_value)
                    new_value_display = str(new_value)

                # Create a human-readable change message
                changes.append(
                    f"{field.replace('_', ' ').capitalize()} changed from '{old_value_display}' to '{new_value_display}'"
                )
            except Exception as e:
                print(f"Error processing field {field}: {str(e)}")

    # Create a TicketAction record if there were any changes
    if changes:
        update_message = "\n".join(changes)
        TicketAction.objects.create(
            ticket=instance,
            action_type='update',
            details=update_message,
            created_by=instance.updated_by,
            is_system_generated=True
        )