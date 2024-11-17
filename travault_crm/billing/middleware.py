from django.shortcuts import redirect
from django.urls import reverse
from billing.models import StripeCustomer

class EnforcePaymentMiddleware:
    """
    Middleware to enforce payment setup after login.
    Exempts admin users, superusers, and specific paths like admin and logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip checks for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip checks for superusers (e.g., admin/developers)
        if request.user.is_superuser:
            return self.get_response(request)

        # Exempt paths like admin, logout, and payment setup
        exempt_paths = [
            reverse('billing:setup_payment'),
            reverse('account_logout'),
            '/admin/',  # Exempt the admin interface
        ]

        # Allow access to exempt paths
        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # Enforce payment setup for regular users
        try:
            stripe_customer = request.user.agency.stripecustomer
            if not stripe_customer.stripe_subscription_id:
                return redirect('billing:setup_payment')
        except (AttributeError, StripeCustomer.DoesNotExist):
            # Redirect if StripeCustomer or agency data is missing
            return redirect('billing:setup_payment')

        return self.get_response(request)
