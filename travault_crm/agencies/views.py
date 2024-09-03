import logging
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
from .forms import AgencyRegistrationForm, UserForm
from .models import CustomUser
from allauth.account.models import EmailAddress
from django.contrib.auth.forms import PasswordResetForm
from allauth.account.utils import send_email_confirmation


logger = logging.getLogger(__name__)

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
        print("CustomLoginView is accessed")  # Debug line
        return super().get(request, *args, **kwargs)

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

def manage_users(request):
    # Get the agency of the logged-in user
    user_agency = request.user.agency

    # Filter users belonging to the same agency and exclude superusers
    users = CustomUser.objects.filter(agency=user_agency, is_superuser=False)

    return render(request, 'users/manage_users.html', {'users': users})

def add_user(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            # Save the user form without committing to the database yet
            new_user = user_form.save(commit=False)
            
            # Link the new user to the current user's agency
            new_user.agency = request.user.agency
            
            # Save the new user to the database
            new_user.save()

            # Manually create EmailAddress object and send confirmation
            email_address = EmailAddress.objects.create(user=new_user, email=new_user.email, primary=True, verified=False)
            send_email_confirmation(request, new_user)

            # Trigger password reset flow to send a password setup email
            password_reset_form = PasswordResetForm({'email': new_user.email})
            if password_reset_form.is_valid():
                password_reset_form.save(
                    request=request,
                    use_https=request.is_secure(),
                    from_email=None,
                    email_template_name='registration/password_reset_email.html',
                    subject_template_name='registration/password_reset_subject.txt',
                    extra_email_context=None,
                )

            messages.success(request, "User has been added successfully!")
            return redirect('agencies:manage_users')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm()

    return render(request, 'users/add_user.html', {
        'user_form': user_form,
    })

def edit_user(request, user_id):
    # Fetch the user object based on the user_id
    user = get_object_or_404(CustomUser, id=user_id)
    original_email = user.email  # Store the original email to check for changes
    
    if request.method == 'POST':
        # Populate the form with the submitted data
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            # Save the changes if the form is valid
            updated_user = user_form.save(commit=False)
            new_email = updated_user.email
            
            # Check if the email address has changed
            if original_email != new_email:
                # Mark the new email as unverified
                EmailAddress.objects.filter(user=updated_user).delete()  # Remove old email records
                email_address = EmailAddress.objects.create(user=updated_user, email=new_email, primary=True, verified=False)
                send_email_confirmation(request, updated_user)  # Send verification email
                
                messages.info(request, "The email address has been changed. A verification email has been sent to the new address.")
            
            # Save the updated user
            updated_user.save()
            
            # Redirect to the manage users page with a success message
            messages.success(request, "User details updated successfully!")
            return redirect('agencies:manage_users')
        else:
            # If the form is not valid, display error messages
            messages.error(request, "Please correct the errors below.")
    else:
        # If the request method is GET, display the form with the user's current data
        user_form = UserForm(instance=user)

    # Render the edit_user.html template with the form
    return render(request, 'users/edit_user.html', {
        'user_form': user_form,
        'edit_user': user  # Pass the user object for the title display
    })