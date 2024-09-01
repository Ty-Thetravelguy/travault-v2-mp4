# agencies/views.py

from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import AgencyRegistrationForm

class AgencyRegistrationView(CreateView):
    template_name = 'agencies/registration.html'
    form_class = AgencyRegistrationForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None) 
        return kwargs