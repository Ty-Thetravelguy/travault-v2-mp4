# billing/webhooks.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from datetime import datetime
import stripe
from agencies.models import Agency
from .models import BillingInvoice
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle incoming webhook events from Stripe.

    This view processes webhook events sent by Stripe, specifically handling
    the 'invoice.paid' event to create a BillingInvoice record in the database.

    Args:
        request (HttpRequest): The incoming HTTP request containing the webhook payload.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the webhook processing.
    """
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        if event.type == 'invoice.paid':
            invoice = event.data.object
            agency = Agency.objects.get(stripecustomer__stripe_customer_id=invoice.customer)
            
            BillingInvoice.objects.create(
                agency=agency,
                stripe_invoice_id=invoice.id,
                amount=invoice.amount_paid / 100,  # Convert from cents
                status='paid',
                invoice_pdf=invoice.invoice_pdf,
                paid_at=datetime.fromtimestamp(invoice.status_transitions.paid_at)
            )
            logger.info(f"Created invoice record for agency {agency.agency_name}")

        return JsonResponse({'status': 'success'})

    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature in Stripe webhook")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except Agency.DoesNotExist as e:
        logger.error(f"Agency not found for Stripe customer: {invoice.customer}")
        return JsonResponse({'error': 'Agency not found'}, status=400)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)