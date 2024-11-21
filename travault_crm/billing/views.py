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
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin', login_url='account_login')
def setup_payment(request):
    try:
        # Ensure the agency exists
        agency = request.user.agency
        if not agency:
            logger.error(f"User {request.user.email} is not associated with an agency.")
            messages.error(request, "Your account is not properly set up. Please contact support.")
            return redirect('billing:billing_error')

        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Check if StripeCustomer exists
        try:
            stripe_customer = agency.stripecustomer
            customer_created = False
        except StripeCustomer.DoesNotExist:
            stripe_customer = None
            customer_created = True

        if request.method == 'POST':
            # Create Stripe customer if necessary
            if not stripe_customer:
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=agency.agency_name,
                )

                # Now create the StripeCustomer instance with required fields
                stripe_customer = StripeCustomer.objects.create(
                    agency=agency,
                    stripe_customer_id=customer.id,
                    stripe_subscription_id='',  # Will be updated after subscription creation
                    subscription_status='pending',  # Changed from 'active' to 'pending'
                )

            # Create a checkout session
            session = stripe.checkout.Session.create(
                customer=stripe_customer.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': agency.users.count(),
                }],
                mode='subscription',
                success_url=request.build_absolute_uri(reverse('billing:setup_payment')) + '?session_id={CHECKOUT_SESSION_ID}',  # Changed to return here first
                cancel_url=request.build_absolute_uri(reverse('billing:setup_payment')),
                metadata={
                    'agency_id': agency.id,
                    'user_count': agency.users.count(),
                },
            )

            return redirect(session.url, code=303)

        elif request.method == 'GET' and 'session_id' in request.GET:
            session = stripe.checkout.Session.retrieve(request.GET['session_id'])
            
            # Verify the session was successful
            if session.payment_status == 'paid':
                # Update the subscription ID and status
                stripe_customer.stripe_subscription_id = session.subscription
                stripe_customer.subscription_status = 'active'
                stripe_customer.save()
                
                messages.success(request, "Payment setup completed successfully!")
                return redirect('dashboard:index')
            else:
                messages.error(request, "Payment was not completed successfully. Please try again.")
                return redirect('billing:setup_payment')

        return render(request, 'billing/setup_payment.html', {'stripe_public_key': settings.STRIPE_PUBLIC_KEY})

    except Exception as e:
        logger.error(f"Unexpected error in setup_payment: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred during payment setup. Please try again.")
        return redirect('billing:billing_error')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        customer_id = invoice['customer']

        # Find the StripeCustomer associated with this customer_id
        try:
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            stripe_customer.subscription_status = 'active'
            stripe_customer.save()

            # Create or update the BillingInvoice
            BillingInvoice.objects.update_or_create(
                stripe_invoice_id=invoice['id'],
                agency=stripe_customer.agency,
                defaults={
                    'amount': invoice['amount_paid'] / 100,  # Convert from cents
                    'status': 'paid',
                    'invoice_pdf': invoice.get('invoice_pdf', ''),
                    'paid_at': timezone.now(),
                }
            )

        except StripeCustomer.DoesNotExist:
            logger.error(f"StripeCustomer with customer_id {customer_id} not found.")

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        customer_id = invoice['customer']

        # Update the subscription status to 'past_due' or 'payment_failed'
        try:
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            stripe_customer.subscription_status = 'past_due'
            stripe_customer.save()

            # Optionally, notify the agency admin about the payment failure

        except StripeCustomer.DoesNotExist:
            logger.error(f"StripeCustomer with customer_id {customer_id} not found.")

    # ... handle other event types as needed ...

    return HttpResponse(status=200)

@login_required
def billing_error(request):
    return render(request, 'billing/billing_error.html')

@login_required
def subscription_inactive(request):
    return render(request, 'billing/subscription_inactive.html')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin', login_url='account_login')
def billing_portal(request):
    try:
        stripe_customer = request.user.agency.stripecustomer
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer.stripe_customer_id,
            return_url=request.build_absolute_uri(reverse('agencies:agency_profile')),
        )
        return redirect(session.url)
    except Exception as e:
        logger.error(f"Error creating billing portal session: {e}")
        messages.error(request, "Failed to load billing portal. Please try again.")
        return redirect('agencies:agency_profile')