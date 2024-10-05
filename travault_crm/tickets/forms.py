from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=[],  # Empty choices initially
        required=False,
        widget=forms.Select(attrs={'disabled': 'disabled', 'class': 'category-field form-select'})
    )
    
    class Meta:
        model = Ticket
        fields = ['company', 'contact', 'priority', 'subject', 'description', 'category_type', 'category']

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        if self.initial.get('company'):
            self.fields['company'].widget.attrs['readonly'] = True

        # Set 'disabled' attribute for the category field
        self.fields['category'].widget.attrs['disabled'] = 'disabled'
        # Add a custom class to identify this field in JavaScript
        self.fields['category'].widget.attrs['class'] = 'category-field form-select'