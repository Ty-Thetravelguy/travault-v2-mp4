# billing/views.py
import os
from dotenv import load_dotenv
import stripe
import logging
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

load_dotenv()

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def setup_payment(request):
    # Add detailed debugging at the start
    print("==== DEBUG STRIPE SETTINGS ====")
    print(f"Direct env var: {os.getenv('STRIPE_PRICE_ID')}")
    print(f"Settings value: {settings.STRIPE_PRICE_ID}")
    print("============================")

    # Debug environment variables
    logger.info("Debugging environment variables:")
    for key, value in os.environ.items():
        if 'STRIPE' in key:
            logger.info(f"{key}: {'*' * len(value) if 'SECRET' in key else value}")

    try:
        # Check if user has an agency
        if not request.user.agency:
            logger.error(f"User {request.user.email} is not associated with an agency.")
            messages.error(request, "Your account is not properly set up. Please contact support.")
            return redirect('billing:billing_error')

        # Check for existing subscription
        stripe_customer = StripeCustomer.objects.filter(agency=request.user.agency).first()
        if stripe_customer and stripe_customer.stripe_subscription_id:
            try:
                # Verify subscription in Stripe
                subscription = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)
                if subscription.status not in ['canceled', 'incomplete_expired']:
                    logger.info(f"Active subscription found: {subscription.id}")
                    messages.info(request, "Your agency already has an active subscription.")
                    return redirect('dashboard:index')
            except stripe.error.StripeError as e:
                logger.error(f"Error retrieving subscription: {str(e)}")

        try:
            # Verify the price exists in Stripe
            price = stripe.Price.retrieve(settings.STRIPE_PRICE_ID)
            logger.info(f"Successfully verified price: {price.id}")
        except stripe.error.StripeError as e:
            logger.error(f"Failed to verify Stripe price: {str(e)}")
            messages.error(request, "Unable to verify payment configuration. Please contact support.")
            return redirect('billing:billing_error')

        # Check user and agency
        if not request.user.agency:
            logger.error(f"User {request.user.email} is not associated with an agency.")
            messages.error(request, "Your account is not properly set up. Please contact support.")
            return redirect('billing:billing_error')
        
        logger.info(f"Processing payment setup for agency: {request.user.agency.agency_name} (ID: {request.user.agency.id})")

        # Get or create Stripe customer
        stripe_customer, created = StripeCustomer.objects.get_or_create(
            agency=request.user.agency,
            defaults={'stripe_customer_id': None}
        )

        if created:
            logger.info(f"Created new StripeCustomer record for agency: {request.user.agency.agency_name}")

        # Create or retrieve Stripe customer
        if not stripe_customer.stripe_customer_id:
            try:
                logger.info("Creating new Stripe customer...")
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=request.user.agency.agency_name,
                    metadata={
                        'agency_id': str(request.user.agency.id),
                        'environment': 'test' if 'test' in settings.STRIPE_SECRET_KEY else 'live'
                    }
                )
                stripe_customer.stripe_customer_id = customer.id
                stripe_customer.save()
                logger.info(f"Created Stripe customer: {customer.id}")
            except stripe.error.StripeError as e:
                logger.error(f"Stripe customer creation failed: {str(e)}")
                messages.error(request, "Failed to set up customer profile. Please try again.")
                return redirect('billing:billing_error')

        # Handle subscription creation
        if not stripe_customer.stripe_subscription_id:
            try:
                logger.info(f"Creating subscription for customer: {stripe_customer.stripe_customer_id}")
                subscription = stripe.Subscription.create(
                    customer=stripe_customer.stripe_customer_id,
                    items=[{
                        'price': settings.STRIPE_PRICE_ID,
                        'quantity': 1,
                    }],
                    payment_behavior='default_incomplete',
                    expand=['latest_invoice.payment_intent'],
                    metadata={
                        'agency_id': str(request.user.agency.id),
                        'environment': 'test' if 'test' in settings.STRIPE_SECRET_KEY else 'live'
                    }
                )
                
                stripe_customer.stripe_subscription_id = subscription.id
                stripe_customer.save()
                logger.info(f"Created subscription: {subscription.id}")

                if not subscription.latest_invoice.payment_intent:
                    logger.error("No payment intent created with subscription")
                    messages.error(request, "Failed to initialize payment. Please try again.")
                    return redirect('billing:billing_error')

                return JsonResponse({
                    'clientSecret': subscription.latest_invoice.payment_intent.client_secret,
                    'subscriptionId': subscription.id
                })
            except stripe.error.StripeError as e:
                logger.error(f"Subscription creation failed: {str(e)}")
                messages.error(request, "Failed to set up subscription. Please try again.")
                return redirect('billing:billing_error')

    except Exception as e:
        logger.error(f"Unexpected error in setup_payment: {str(e)}", exc_info=True)
        messages.error(request, "An unexpected error occurred. Please try again or contact support.")
        return redirect('billing:billing_error')

    # Render the payment form if no subscription needs to be created
    return render(request, 'billing/setup_payment.html', {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'CUSTOMER_EMAIL': request.user.email,
        'AGENCY_NAME': request.user.agency.agency_name
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

@login_required
def billing_error(request):
    return render(request, 'billing/billing_error.html')