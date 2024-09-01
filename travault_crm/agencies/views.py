import logging
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import AgencyRegistrationForm

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
class AgencyRegistrationView(CreateView):
    template_name = 'agencies/registration.html'
    form_class = AgencyRegistrationForm
    success_url = reverse_lazy('home')

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