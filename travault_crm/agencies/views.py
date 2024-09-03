import logging
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.contrib import messages
from allauth.account.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView, PasswordResetFromKeyDoneView

from .forms import AgencyRegistrationForm

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

from django.shortcuts import render
from agencies.models import CustomUser

def manage_users(request):
    # Get the agency of the logged-in user
    user_agency = request.user.agency

    # Filter users belonging to the same agency and exclude superusers
    users = CustomUser.objects.filter(agency=user_agency, is_superuser=False)

    return render(request, 'users/manage_users.html', {'users': users})
