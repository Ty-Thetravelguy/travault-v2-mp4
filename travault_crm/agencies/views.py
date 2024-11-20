import logging
import time
import stripe
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

logger = logging.getLogger(__name__)
User = get_user_model()

class AgencyRegistrationView(SignupView):
    template_name = 'agencies/registration.html'
    form_class = AgencyRegistrationForm
    success_url = reverse_lazy('account_email_verification_sent')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None)  # Ensure no unintended 'instance' is passed
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        try:
            # Create user and agency in one transaction
            logger.debug("Form validation successful. Starting user and agency creation.")
            user = form.save(self.request)
            
            if not user.agency:
                logger.error(f"Agency not created for user {user.email}")
                messages.error(self.request, "Failed to create agency. Please try again.")
                return self.form_invalid(form)
            
            # Set user as admin
            user.user_type = 'admin'
            user.save()
            
            logger.info(f"Successfully created agency {user.agency.agency_name} with admin user {user.email}")
            messages.success(self.request, "Registration successful! Please verify your email.")
            
            # Send verification email
            try:
                send_email_confirmation(self.request, user)
                logger.info(f"Verification email sent to {user.email}")
            except Exception as email_error:
                logger.error(f"Failed to send verification email: {str(email_error)}")
                # Continue with registration even if email fails
                
            return super().form_valid(form)
            
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}", exc_info=True)
            messages.error(self.request, "An error occurred during registration. Please try again.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        try:
            ret = super().get_context_data(**kwargs)
            ret.update(self.kwargs)
            
            # Add any additional context needed for the template
            ret['page_title'] = 'Agency Registration'
            ret['form_title'] = 'Register Your Agency'
            
            return ret
            
        except Exception as e:
            logger.error(f"Error getting context data: {str(e)}", exc_info=True)
            return super().get_context_data(**kwargs)

    def get_success_url(self):
        try:
            # You can customize the success URL based on conditions
            return str(self.success_url)
        except Exception as e:
            logger.error(f"Error getting success URL: {str(e)}", exc_info=True)
            return str(reverse_lazy('account_email_verification_sent'))


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
    logger.info("Entering profile_view.")
    start_time = time.time()

    # Fetch the current user and their original email address
    user = request.user
    original_email = user.email
    logger.debug(f"Fetched user: {user.username} with email: {original_email}")

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        # Exclude fields that should not be editable in the profile context
        form.fields.pop('username', None)
        form.fields.pop('user_type', None)

        if form.is_valid():
            updated_user = form.save(commit=False)
            new_email = updated_user.email

            # Check if the email address has changed
            if original_email != new_email:
                logger.info(f"Email address change detected for user: {user.username}")
                # Mark the new email as unverified
                EmailAddress.objects.filter(user=updated_user).delete()  # Remove old email records
                EmailAddress.objects.create(user=updated_user, email=new_email, primary=True, verified=False)
                send_email_confirmation(request, updated_user)  # Send verification email
                logger.info(f"Verification email sent to new address: {new_email}")

                messages.info(request, "The email address has been changed. A verification email has been sent to the new address.")

            updated_user.save()
            logger.info(f"Profile updated for user: {user.username}")
            messages.success(request, "Profile updated successfully!")
            return redirect('/agencies/profile/')  # Adjust to your profile URL name
        else:
            logger.error(f"Profile update failed with errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")

    # Initialize the form for GET requests
    else:
        form = UserForm(instance=user)
        # Exclude fields that should not be editable in the profile context
        form.fields.pop('username', None)
        form.fields.pop('user_type', None)
        logger.debug("Initialized form for profile update.")

    # Update the template path to match your actual template location
    logger.info(f"profile_view completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'users/profile.html', {'form': form})


@login_required
def agency_profile(request):
    user = request.user
    agency = user.agency

    # Handle the agency details form
    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, request.FILES, instance=agency)
        if form.is_valid():
            form.save()
            messages.success(request, "Agency details updated successfully.")
            return redirect('agencies:agency_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AgencyProfileForm(instance=agency)

    # Calculate subscription details
    user_count = agency.customuser_set.count()
    total_monthly_charge = user_count * 9.00  # Assuming £9 per user

    # Retrieve payment method (for admin users)
    payment_method = None
    if user.user_type == 'admin':
        try:
            stripe_customer = agency.stripecustomer
            payment_methods = stripe.PaymentMethod.list(
                customer=stripe_customer.stripe_customer_id,
                type="card"
            )
            if payment_methods.data:
                payment_method = payment_methods.data[0]
        except Exception as e:
            logger.error(f"Error retrieving payment method: {e}")

    # Retrieve invoices
    invoices = BillingInvoice.objects.filter(agency=agency).order_by('-created_at')[:5]

    context = {
        'form': form,
        'user_count': user_count,
        'total_monthly_charge': total_monthly_charge,
        'payment_method': payment_method,
        'invoices': invoices,
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
    logger.info("Entering manage_users view.")
    start_time = time.time()

    # Fetch users associated with the user's agency, excluding superusers
    user_agency = request.user.agency
    users = CustomUser.objects.filter(agency=user_agency, is_superuser=False)
    logger.debug(f"Fetched {users.count()} users for agency '{user_agency.agency_name}'.")

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
    logger.info("Entering add_user view.")
    start_time = time.time()

    # Handle form submission for adding a new user
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.agency = request.user.agency
            new_user.save()
            logger.info(f"New user '{new_user.username}' added to agency '{new_user.agency.name}'.")

            # Create the email confirmation object
            EmailAddress.objects.create(user=new_user, email=new_user.email, primary=True, verified=False)
            logger.debug(f"Email confirmation object created for user '{new_user.username}'.")

            # Generate the token and uid for the confirmation link
            token = default_token_generator.make_token(new_user)
            uid = urlsafe_base64_encode(force_bytes(new_user.pk))

            # Construct the confirmation URL
            confirm_url = request.build_absolute_uri(
                reverse('agencies:confirm_email_and_setup_password', args=[uid, token])
            )
            logger.debug(f"Confirmation URL generated for user '{new_user.username}': {confirm_url}")

            # Send the custom confirmation email
            context = {
                'user': new_user,
                'site_name': 'TraVault',
                'confirm_url': confirm_url,
            }

            # Ensure the template path is correct and accessible
            email_subject = 'Confirm Your Email and Set Your Password'
            email_body = render_to_string('account/custom_account_confirmation_email.html', context)

            send_mail(
                email_subject,
                email_body,
                'no-reply@example.com',  # Replace with your sender email
                [new_user.email],
                fail_silently=False,
            )
            logger.info(f"Confirmation email sent to '{new_user.email}'.")

            messages.success(request, "User has been added successfully and an email has been sent to confirm and set up the password!")
            return redirect('agencies:manage_users')
        else:
            logger.error(f"Form validation errors: {user_form.errors}")
            messages.error(request, "Please correct the errors below.")

    # Initialize the form for GET requests
    else:
        user_form = UserForm()
        logger.debug("Initialized form for adding a new user.")

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
    logger.info(f"Entering edit_user view for user_id={user_id}.")
    start_time = time.time()

    # Fetch the user to be edited
    user = get_object_or_404(CustomUser, id=user_id)
    original_email = user.email
    logger.debug(f"Fetched user: {user.username} with original email: {original_email}.")

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            updated_user = user_form.save(commit=False)
            new_email = updated_user.email

            # Check if the email address has changed
            if original_email != new_email:
                logger.info(f"Email address change detected for user: {user.username}.")
                # Mark the new email as unverified
                EmailAddress.objects.filter(user=updated_user).delete()
                email_address = EmailAddress.objects.create(user=updated_user, email=new_email, primary=True, verified=False)
                send_email_confirmation(request, updated_user)
                logger.info(f"Verification email sent to new address: {new_email}.")

                messages.info(request, "The email address has been changed. A verification email has been sent to the new address.")

            updated_user.save()
            logger.info(f"User details updated successfully for user: {user.username}.")
            messages.success(request, "User details updated successfully!")
            return redirect('agencies:manage_users')
        else:
            logger.error(f"Form validation errors: {user_form.errors}.")
            messages.error(request, "Please correct the errors below.")

    # Initialize the form for GET requests
    else:
        user_form = UserForm(instance=user)
        logger.debug("Initialized form for editing user.")

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
    logger.info(f"Entering delete_user view for user_id={user_id}.")
    start_time = time.time()

    # Fetch the user to be deleted
    user = get_object_or_404(CustomUser, id=user_id)
    logger.debug(f"Fetched user: {user.username} for deletion.")

    if request.method == 'POST':
        confirmation_name = request.POST.get('confirmation_name')
        if confirmation_name == user.username:
            user.delete()
            logger.info(f"User '{user.username}' has been deleted successfully.")
            messages.success(request, "User has been deleted successfully!")
            return redirect('agencies:manage_users')
        else:
            logger.warning(f"Username confirmation failed for deleting user '{user.username}'.")
            messages.error(request, "The username entered does not match. Please try again.")

    logger.info(f"delete_user completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'users/delete_user.html', {
        'delete_user': user
    })


def confirm_email_and_setup_password(request, uidb64, token):
    """
    View to confirm email and allow the user to set their password.

    This view is used after a user clicks on an email confirmation link. It verifies
    the token and allows the user to set a new password if the link is valid. If the
    link is invalid or expired, an error message is displayed.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        uidb64 (str): Base64 encoded user ID.
        token (str): Token to verify the user's email.

    Returns:
        HttpResponse: Renders the setup_password template with the password form,
        or redirects to the login view on success or error.
    """
    logger.info(f"Entering confirm_email_and_setup_password with uidb64={uidb64}.")
    start_time = time.time()

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(CustomUser, pk=uid)
        logger.debug(f"Fetched user: {user.username} for email confirmation and password setup.")

        if default_token_generator.check_token(user, token):
            email_address = EmailAddress.objects.filter(user=user, email=user.email).first()
            if email_address and not email_address.verified:
                email_address.verified = True
                email_address.save()
                logger.info(f"Email address '{email_address.email}' verified for user '{user.username}'.")

            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
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
                            if user.user_type == 'admin':
                                return redirect('billing:setup_payment')
                            else:
                                return redirect('billing:subscription_inactive')
                    except StripeCustomer.DoesNotExist:
                        if user.user_type == 'admin':
                            messages.error(request, "Please complete payment setup for your agency.")
                            return redirect('billing:setup_payment')
                        else:
                            messages.error(request, "Your agency has not completed payment setup. Please contact your administrator.")
                            return redirect('billing:subscription_inactive')

        else:
            logger.warning(f"Invalid or expired token for user '{user.username}'.")
            messages.error(request, "The confirmation link is invalid or has expired.")
            return redirect('account_login')

    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        logger.error("Invalid confirmation link.")
        messages.error(request, "The confirmation link is invalid.")
        return redirect('account_login')