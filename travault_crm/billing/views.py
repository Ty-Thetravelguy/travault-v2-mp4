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
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get the stripe customer
        stripe_customer = request.user.agency.stripecustomer
        
        # Create Stripe billing portal session
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer.stripe_customer_id,
            return_url=request.build_absolute_uri(reverse('agencies:agency_profile')),
        )
        
        # Return the URL as JSON
        return JsonResponse({'url': session.url})
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating billing portal session: {str(e)}")
        return JsonResponse({
            'error': 'Unable to access billing portal. Please try again later.'
        }, status=500)
    except Exception as e:
        logger.error(f"Error creating billing portal session: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'An unexpected error occurred. Please contact support.'
        }, status=500)
    
@login_required
def create_setup_intent(request):
    try:
        stripe_customer = request.user.agency.stripecustomer
        setup_intent = stripe.SetupIntent.create(
            customer=stripe_customer.stripe_customer_id,
            payment_method_types=['card'],
        )
        return JsonResponse({
            'client_secret': setup_intent.client_secret
        })
    except Exception as e:
        logger.error(f"Error creating setup intent: {e}")
        return JsonResponse({'error': str(e)}, status=500)