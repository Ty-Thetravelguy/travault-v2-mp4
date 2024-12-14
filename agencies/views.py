import logging
import time
import stripe
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import AgencyRegistrationForm, UserForm, AgencyProfileForm
from .models import CustomUser, Agency
from allauth.account.views import (
    SignupView,
    LoginView, 
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetFromKeyView, 
    PasswordResetFromKeyDoneView,
)
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.account.models import EmailAddress
from django.contrib.auth.forms import PasswordResetForm
from allauth.account.utils import send_email_confirmation
from allauth.account.utils import setup_user_email
from allauth.account.adapter import get_adapter
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.db import transaction
from billing.models import StripeCustomer
from django.contrib.auth import login
from billing.models import BillingInvoice
from django.http import JsonResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)
User = get_user_model()

class AgencyRegistrationView(SignupView):
    """
    View for handling agency registration.

    This view extends the SignupView to include additional functionality
    for registering an agency along with the user.
    """
    template_name = 'agencies/registration.html'
    form_class = AgencyRegistrationForm
    success_url = reverse_lazy('agencies:registration_success')

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.

        This method ensures that no unintended 'instance' is passed to the form.

        Returns:
            dict: The keyword arguments for the form.
        """
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None)  # Ensure no unintended 'instance' is passed
        return kwargs

    def form_invalid(self, form):
        """
        Handles the case when the form is invalid.

        This method logs the form errors and returns the invalid form.

        Args:
            form: The invalid form instance.

        Returns:
            HttpResponse: The response for the invalid form.
        """
        messages.error(self.request, "There were errors in your submission. Please correct them.")
        return super().form_invalid(form)

    @transaction.atomic
    def form_valid(self, form):
        """
        Handles the case when the form is valid.

        This method creates a user and an agency in a single transaction,
        sends a verification email, and redirects to the success URL.

        Args:
            form: The valid form instance.

        Returns:
            HttpResponse: The response for the valid form.
        """
        try:
            # Create user and agency in one transaction
            user = form.save(self.request)

            if not user.agency:
                messages.error(self.request, "Failed to create agency. Please try again.")
                return self.form_invalid(form)
            
            # Set user as admin
            user.user_type = 'admin'
            user.save()

            # Send success message
            messages.success(self.request, "Registration successful! Please verify your email.")
            
            # Send verification email
            send_email_confirmation(self.request, user)

            # Redirect to your success page instead of the allauth default
            return HttpResponseRedirect(self.get_success_url())
        
        except Exception as e:
            messages.error(self.request, "An error occurred during registration. Please try again.")
            if 'user' in locals() and user.id:
                try:
                    user.delete()
                except Exception:
                    pass  # Handle cleanup error silently
            return self.form_invalid(form)
        
    def get_context_data(self, **kwargs):
        """
        Adds additional context to the registration template.

        Args:
            kwargs: Additional keyword arguments.

        Returns:
            dict: The context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        
        # Add additional context if needed
        context['page_title'] = 'Agency Registration'
        context['form_title'] = 'Register Your Agency'
        return context

    def get_success_url(self):
        """
        Returns the success URL for the registration.

        This method can be customized based on conditions.

        Returns:
            str: The success URL.
        """
        return str(self.success_url)


def registration_success(request):
    """
    View to display registration success page.
    """
    return render(request, 'agencies/registration_success.html')


class CustomLoginView(LoginView):
    """
    Custom login view to handle user authentication.

    This view renders the login page and handles the login process using the default
    functionality provided by Django's LoginView.
    """
    template_name = 'account/account_login.html'

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to render the login form.

        Args:
            request (HttpRequest): The incoming HTTP request from the client.

        Returns:
            HttpResponse: A response rendering the login form.
        """
        logger.info("Rendering login form.")
        return super().get(request, *args, **kwargs)


@login_required
def profile_view(request):
    """
    View to display and update the user's profile.

    This view allows users to view and update their profile information. It handles
    both GET requests for displaying the current profile details and POST requests for
    updating the profile. Special handling is included for updating email addresses.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the profile template with the profile form,
        or redirects to the profile view on successful update.
    """
    start_time = time.time()

    user = request.user
    original_email = user.email

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        form.fields.pop('username', None)
        form.fields.pop('user_type', None)

        if form.is_valid():
            new_email = form.cleaned_data.get('email')

            # Check if email has changed
            if original_email != new_email:
                # Check if email exists in CustomUser model
                if CustomUser.objects.filter(email=new_email).exclude(id=user.id).exists():
                    messages.error(request, "This email address is already registered. Please use a different email.")
                    return render(request, 'users/profile.html', {'form': form})

                # Check if email exists in EmailAddress model
                if EmailAddress.objects.filter(email=new_email).exists():
                    messages.error(request, "This email address is already in use. Please use a different email.")
                    return render(request, 'users/profile.html', {'form': form})

                # If we get here, email is unique and we can proceed
                updated_user = form.save(commit=False)
                updated_user.email = original_email  # Keep original email for now
                updated_user.save()

                # Handle email verification
                EmailAddress.objects.filter(user=user).delete()
                EmailAddress.objects.create(
                    user=user,
                    email=new_email,
                    primary=True,
                    verified=False
                )
                send_email_confirmation(request, user)
                messages.info(request, "A verification email has been sent to your new email address.")
            else:
                # No email change, just save the form
                form.save()
                messages.success(request, "Profile updated successfully!")

            return redirect('/agencies/profile/')
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = UserForm(instance=user)
        form.fields.pop('username', None)
        form.fields.pop('user_type', None)

    logger.info(f"profile_view completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'users/profile.html', {'form': form})


@login_required
def agency_profile(request):
    """
    View to display and update the agency's profile.

    This view allows users to view and update their agency's profile information.
    It handles both GET requests for displaying the current agency details and POST
    requests for updating the agency profile.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the agency profile template with the agency form,
        or redirects to the agency profile view on successful update.
    """
    agency = request.user.agency
    
    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, instance=agency)
        if form.is_valid():
            form.save()
            messages.success(request, "Agency details updated successfully.")
            return redirect('agencies:agency_profile')
    else:
        form = AgencyProfileForm(instance=agency)

    # Get user count and calculate charges
    user_count = agency.users.count()
    total_monthly_charge = user_count * 9.00

    # Get Stripe payment method
    stripe_payment_method = None
    try:
        stripe_customer = agency.stripecustomer
        if stripe_customer.stripe_customer_id:
            payment_methods = stripe.PaymentMethod.list(
                customer=stripe_customer.stripe_customer_id,
                type="card"
            )
            if payment_methods.data:
                stripe_payment_method = payment_methods.data[0].card
    except Exception as e:
        logger.error(f"Error retrieving payment method: {e}")

    # Get recent invoices
    invoices = BillingInvoice.objects.filter(agency=agency).order_by('-created_at')[:5]

    context = {
        'form': form,
        'user_count': user_count,
        'total_monthly_charge': total_monthly_charge,
        'stripe_payment_method': stripe_payment_method,
        'invoices': invoices,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, 'agencies/agency_profile.html', context)


@method_decorator(login_required, name='dispatch')
class CustomLogoutView(LogoutView):
    """
    Custom logout view to handle user logout.

    This view renders a custom logout template upon logging out the user.
    """
    template_name = 'account/account_logout.html'


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view to initiate password reset process.

    This view renders a custom password reset template and handles the sending
    of password reset emails to users who request it.
    """
    template_name = 'account/password_reset.html'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Custom view to display the password reset done page.

    This view renders a custom template confirming that the password reset email
    has been sent to the user.
    """
    template_name = 'account/password_reset_done.html'


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    """
    Custom view to handle password reset using a key from the email.

    This view allows users to reset their password using a link received in
    their email after initiating a password reset.
    """
    template_name = 'account/password_reset_from_key.html'


class CustomPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    """
    Custom view to display the password reset completion page.

    This view renders a custom template confirming that the password has been
    successfully reset using the key from the email.
    """
    template_name = 'account/password_reset_from_key_done.html'


@login_required
def manage_users(request):
    """
    View to manage users within the current user's agency.

    This view displays a list of users associated with the agency, excluding
    superusers, and allows the admin to manage these users.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the manage_users template with a list of users.
    """
    start_time = time.time()

    # Fetch users associated with the user's agency, excluding superusers
    user_agency = request.user.agency
    users = CustomUser.objects.filter(agency=user_agency, is_superuser=False)

    logger.info(f"manage_users completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'users/manage_users.html', {'users': users})


@login_required
def add_user(request):
    """
    View to add a new user to the current user's agency.

    This view allows the admin to add new users by submitting a form. It handles
    both GET requests for displaying the blank form and POST requests for creating
    the new user. Upon successful addition, it sends a confirmation email for the
    new user to set their password.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the add_user template with the form, or redirects
        to the manage users view on successful addition.
    """
    start_time = time.time()

    # Handle form submission for adding a new user
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.agency = request.user.agency
            new_user.save()

            # Create the email confirmation object
            EmailAddress.objects.create(user=new_user, email=new_user.email, primary=True, verified=False)

            # Generate the token and uid for the confirmation link
            token = default_token_generator.make_token(new_user)
            uid = urlsafe_base64_encode(force_bytes(new_user.pk))

            # Construct the confirmation URL
            confirm_url = request.build_absolute_uri(
                reverse('agencies:confirm_email_and_setup_password', args=[uid, token])
            )

            # Send the custom confirmation email
            context = {
                'user': new_user,
                'site_name': 'TraVault',
                'confirm_url': confirm_url,
            }

            email_subject = 'Confirm Your Email and Set Your Password'
            email_body = render_to_string('account/custom_account_confirmation_email.html', context)

            send_mail(
                email_subject,
                email_body,
                'no-reply@travault.com', 
                [new_user.email],
                fail_silently=False,
            )

            messages.success(request, "User has been added successfully and an email has been sent to confirm and set up the password!")
            return redirect('agencies:manage_users')
        else:
            messages.error(request, "Please correct the errors below.")

    # Initialize the form for GET requests
    else:
        user_form = UserForm()

    logger.info(f"add_user completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'users/add_user.html', {'user_form': user_form})


@login_required
def edit_user(request, user_id):
    """
    View to edit user details.

    This view allows admins to update a user's details. It handles both GET requests
    for displaying the current user details and POST requests for updating the user
    information. Special handling is included for email address changes, triggering
    a verification email.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        user_id (int): The ID of the user to be edited.

    Returns:
        HttpResponse: Renders the edit_user template with the form,
        or redirects to the manage users view on successful update.
    """
    start_time = time.time()

    # Fetch the user to be edited
    user = get_object_or_404(CustomUser, id=user_id)
    original_email = user.email

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            updated_user = user_form.save(commit=False)
            new_email = updated_user.email

            # Check if the email address has changed
            if original_email != new_email:
                # Mark the new email as unverified
                EmailAddress.objects.filter(user=updated_user).delete()
                EmailAddress.objects.create(user=updated_user, email=new_email, primary=True, verified=False)
                send_email_confirmation(request, updated_user)

                messages.info(request, "The email address has been changed. A verification email has been sent to the new address.")

            updated_user.save()
            messages.success(request, "User details updated successfully!")
            return redirect('agencies:manage_users')
        else:
            messages.error(request, "Please correct the errors below.")

    # Initialize the form for GET requests
    else:
        user_form = UserForm(instance=user)

    logger.info(f"edit_user completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'users/edit_user.html', {
        'user_form': user_form,
        'edit_user': user
    })


@login_required
def delete_user(request, user_id):
    """
    View to delete a specific user.

    This view allows admins to delete a user by confirming their username. It handles
    the deletion upon POST request and redirects back to the manage users view.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        user_id (int): The ID of the user to be deleted.

    Returns:
        HttpResponse: Redirects to the manage users view on successful deletion,
        or renders the delete_user template for confirmation.
    """
    start_time = time.time()

    # Fetch the user to be deleted
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        confirmation_name = request.POST.get('confirmation_name')
        if confirmation_name == user.username:
            user.delete()
            messages.success(request, "User has been deleted successfully!")
            return redirect('agencies:manage_users')
        else:
            messages.error(request, "The username entered does not match. Please try again.")

    logger.info(f"delete_user completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'users/delete_user.html', {
        'delete_user': user
    })


def confirm_email_and_setup_password(request, uidb64, token):
    """
    View to confirm email and allow the user to set their password.

    This view processes the email confirmation link, verifies the token, and allows
    the user to set their password if the token is valid.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        uidb64 (str): The base64 encoded user ID.
        token (str): The token for confirming the email.

    Returns:
        HttpResponse: Renders the setup password template or redirects to the login page
        if the confirmation link is invalid or expired.
    """
    logger.info("=== Starting Email Confirmation Process ===")

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(CustomUser, pk=uid)
        
        is_valid = default_token_generator.check_token(user, token)

        if is_valid:
            email_address = EmailAddress.objects.filter(user=user, email=user.email).first()
            
            if email_address and not email_address.verified:
                email_address.verified = True
                email_address.save()

            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                
                if form.is_valid():
                    form.save()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    messages.success(request, "Your password has been set successfully!")

                    try:
                        agency = user.agency
                        stripe_customer = agency.stripecustomer
                        subscription = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)

                        if subscription.status in ['active', 'trialing']:
                            return redirect('dashboard:index')
                        else:
                            messages.error(request, "Your agency's subscription is not active.")
                            return redirect('billing:setup_payment' if user.user_type == 'admin' else 'billing:subscription_inactive')
                    except StripeCustomer.DoesNotExist:
                        messages.error(request, "Please complete payment setup for your agency." if user.user_type == 'admin' else "Your agency has not completed payment setup. Please contact your administrator.")
                        return redirect('billing:setup_payment' if user.user_type == 'admin' else 'billing:subscription_inactive')
                else:
                    messages.error(request, "Please correct the errors below.")
            else:
                form = SetPasswordForm(user)

            return render(request, 'account/setup_password.html', {
                'form': form,
                'uidb64': uidb64,
                'token': token,
                'user': user
            })
        else:
            messages.error(request, "The confirmation link is invalid or has expired. Please request a new one.")
            return redirect('account_login')

    except Exception as e:
        logger.error(f"Error in email confirmation process: {str(e)}", exc_info=True)
        messages.error(request, "The confirmation link is invalid. Please request a new one.")
        return redirect('account_login')


@require_POST
def resend_verification_email(request):
    """
    View to resend the verification email to the user.

    This view handles the POST request to resend the verification email
    to the currently authenticated user. It provides feedback on the
    success or failure of the email sending process.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Redirects to the registration success page.
    """
    try:
        send_email_confirmation(request, request.user)
        messages.success(request, "A new verification email has been sent. Please check your inbox.")
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        messages.error(request, "There was an error sending the verification email. Please try again or contact support.")
    
    return redirect('agencies:registration_success')