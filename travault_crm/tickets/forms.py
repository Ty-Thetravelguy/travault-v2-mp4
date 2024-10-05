from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['company', 'contact', 'priority', 'description']

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        if self.initial.get('company'):
            # Make the company field read-only if pre-filled
            self.fields['company'].widget.attrs['readonly'] = True
