import logging
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.contrib import messages
from allauth.account.views import (
    LoginView, 
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetFromKeyView, 
    PasswordResetFromKeyDoneView
)
from .forms import AgencyRegistrationForm, UserForm, AgencyProfileForm
from .models import CustomUser
from allauth.account.models import EmailAddress
from django.contrib.auth.forms import PasswordResetForm
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm

logger = logging.getLogger(__name__)
User = get_user_model()

@method_decorator(csrf_protect, name='dispatch')
class AgencyRegistrationView(CreateView):
    template_name = 'agencies/registration.html'
    form_class = AgencyRegistrationForm
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None) 
        return kwargs

    def form_valid(self, form):
        try:
            self.object = form.save(self.request)
            messages.success(self.request, "Registration successful!")
            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            messages.error(self.request, "An error occurred during registration. Please try again.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.error(f"Form validation failed: {form.errors}")
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

class CustomLoginView(LoginView):
    template_name = 'account/account_login.html'
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@login_required
def profile_view(request):
    user = request.user
    original_email = user.email

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        # Exclude fields you don't want to be editable in the profile context
        form.fields.pop('username', None)
        form.fields.pop('user_type', None)

        if form.is_valid():
            updated_user = form.save(commit=False)
            new_email = updated_user.email

            # Check if the email address has changed
            if original_email != new_email:
                # Mark the new email as unverified
                EmailAddress.objects.filter(user=updated_user).delete()  # Remove old email records
                EmailAddress.objects.create(user=updated_user, email=new_email, primary=True, verified=False)
                send_email_confirmation(request, updated_user)  # Send verification email

                messages.info(request, "The email address has been changed. A verification email has been sent to the new address.")

            updated_user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('/agencies/profile/')  # Adjust to your profile URL name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserForm(instance=user)
        # Exclude fields you don't want to be editable in the profile context
        form.fields.pop('username', None)
        form.fields.pop('user_type', None)

    # Update the template path to match your actual template location
    return render(request, 'users/profile.html', {'form': form})


@login_required
def agency_profile_view(request):
    # Ensure the user is an admin
    if request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('agencies:manage_users')

    agency = request.user.agency

    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, instance=agency)
        if form.is_valid():
            form.save()
            messages.success(request, "Agency profile updated successfully!")
            return redirect('agencies:agency_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AgencyProfileForm(instance=agency)

    return render(request, 'agencies/agency_profile.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class CustomLogoutView(LogoutView):
    template_name = 'account/account_logout.html'

class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/password_reset.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    template_name = 'account/password_reset_from_key.html'

class CustomPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    template_name = 'account/password_reset_from_key_done.html'

@login_required
def manage_users(request):
    user_agency = request.user.agency
    users = CustomUser.objects.filter(agency=user_agency, is_superuser=False)
    return render(request, 'users/manage_users.html', {'users': users})

@login_required
def add_user(request):
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

            # Correct confirmation URL to match your defined URL pattern
            confirm_url = request.build_absolute_uri(
                reverse('agencies:confirm_email_and_setup_password', args=[uid, token])
            )

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

            messages.success(request, "User has been added successfully and an email has been sent to confirm and set up the password!")
            return redirect('agencies:manage_users')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm()

    return render(request, 'users/add_user.html', {'user_form': user_form})

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    original_email = user.email
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            updated_user = user_form.save(commit=False)
            new_email = updated_user.email
            
            if original_email != new_email:
                EmailAddress.objects.filter(user=updated_user).delete()
                email_address = EmailAddress.objects.create(user=updated_user, email=new_email, primary=True, verified=False)
                send_email_confirmation(request, updated_user)
                
                messages.info(request, "The email address has been changed. A verification email has been sent to the new address.")
            
            updated_user.save()
            messages.success(request, "User details updated successfully!")
            return redirect('agencies:manage_users')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm(instance=user)

    return render(request, 'users/edit_user.html', {
        'user_form': user_form,
        'edit_user': user
    })

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        confirmation_name = request.POST.get('confirmation_name')
        if confirmation_name == user.username:
            user.delete()
            messages.success(request, "User has been deleted successfully!")
            return redirect('agencies:manage_users')
        else:
            messages.error(request, "The username entered does not match. Please try again.")

    return render(request, 'users/delete_user.html', {
        'delete_user': user
    })

def confirm_email_and_setup_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)

        if default_token_generator.check_token(user, token):
            email_address = EmailAddress.objects.filter(user=user, email=user.email).first()
            if email_address and not email_address.verified:
                email_address.verified = True
                email_address.save()

            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your password has been set successfully! You can now log in.")
                    return redirect('account_login')
            else:
                form = SetPasswordForm(user)

            return render(request, 'account/setup_password.html', {'form': form})

        else:
            messages.error(request, "The confirmation link is invalid or has expired.")
            return redirect('account_login')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "The confirmation link is invalid.")
        return redirect('account_login')
