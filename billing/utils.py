from django.core.mail import send_mail
from django.conf import settings
from .models import Agency 
import logging

logger = logging.getLogger(__name__)

def send_invoice_email(agency_id, invoice_pdf):
    # Fetch the agency from the database
    try:
        agency = Agency.objects.get(id=agency_id)

        # Use the `email` field from the `Agency` model
        contact_email = agency.email
        contact_name = agency.contact_name

        # Log the contact information for debugging purposes
        logger.info(f"Sending invoice email to {contact_name} ({contact_email}) for agency {agency.agency_name}")

        # Send the email
        send_mail(
            subject="Your Invoice",
            message=f"Dear {contact_name},\n\nPlease find your invoice attached: {invoice_pdf}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_email], 
            fail_silently=False,
        )
        logger.info(f"Invoice email sent successfully to {contact_email} for agency {agency.agency_name}.")
    
    except Agency.DoesNotExist:
        logger.error(f"Agency with ID {agency_id} not found.")
    except Exception as e:
        logger.error(f"Error sending invoice email: {str(e)}", exc_info=True)