# billing/views.py
import stripe
from .models import StripeCustomer, BillingInvoice
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .utils import send_invoice_email

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def setup_payment(request):
    if request.method == 'POST':
        try:
            # Create or get Stripe customer
            if not hasattr(request.user.agency, 'stripecustomer'):
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=request.user.agency.agency_name,
                    metadata={'agency_id': request.user.agency.id}
                )
                
                # Create subscription
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{'price': settings.STRIPE_PRICE_ID}],  # Monthly per-user price
                    payment_behavior='default_incomplete',
                    expand=['latest_invoice.payment_intent'],
                    metadata={'agency_id': request.user.agency.id}
                )
                
                # Save Stripe customer info
                StripeCustomer.objects.create(
                    agency=request.user.agency,
                    stripe_customer_id=customer.id,
                    stripe_subscription_id=subscription.id
                )
                
                return JsonResponse({
                    'clientSecret': subscription.latest_invoice.payment_intent.client_secret
                })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return render(request, 'billing/setup_payment.html', {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    })

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        agency_id = invoice['subscription']['metadata']['agency_id']
        
        # Create invoice record
        BillingInvoice.objects.create(
            agency_id=agency_id,
            stripe_invoice_id=invoice['id'],
            amount=invoice['amount_paid'] / 100,  # Convert from cents
            status='paid',
            invoice_pdf=invoice['invoice_pdf'],
            paid_at=timezone.now()
        )
        
        # Send invoice email
        send_invoice_email(agency_id, invoice['invoice_pdf'])

    return HttpResponse(status=200)