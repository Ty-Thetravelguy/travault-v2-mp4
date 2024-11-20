# billing/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from billing.models import StripeCustomer
from django.conf import settings
import stripe
import logging

logger = logging.getLogger(__name__)

class EnforcePaymentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.user.is_superuser:
            return self.get_response(request)

        exempt_paths = [
            reverse('billing:setup_payment'),
            reverse('account_logout'),
            reverse('account_email_verification_sent'),
            reverse('account_confirm_email', args=['placeholder']),
            reverse('account_reset_password'),
            reverse('account_reset_password_done'),
            reverse('account_reset_password_from_key', args=['placeholder', 'placeholder']),
            reverse('account_reset_password_from_key_done'),
            '/admin/',
        ]

        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        if not request.user.emailaddress_set.filter(verified=True).exists():
            messages.info(request, "Please verify your email address to proceed.")
            return redirect('account_email_verification_sent')

        try:
            agency = request.user.agency
            stripe_customer = agency.stripecustomer

            subscription = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)

            if subscription.status not in ['active', 'trialing']:
                messages.error(request, "Your agency's subscription is not active.")
                if request.user.user_type == 'admin':
                    return redirect('billing:setup_payment')
                else:
                    return redirect('billing:subscription_inactive')
        except StripeCustomer.DoesNotExist:
            if request.user.user_type == 'admin':
                messages.error(request, "Please complete payment setup for your agency.")
                return redirect('billing:setup_payment')
            else:
                messages.error(request, "Your agency has not completed payment setup. Please contact your administrator.")
                return redirect('billing:subscription_inactive')
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            messages.error(request, "Unable to verify subscription status. Please try again later.")
            return redirect('billing:billing_error')
        except AttributeError:
            messages.error(request, "Your account is not properly set up. Please contact support.")
            return redirect('account_logout')

        return self.get_response(request)