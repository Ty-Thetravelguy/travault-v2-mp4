from django import forms
from .models import Ticket, TicketSubject

class TicketForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    category = forms.ChoiceField(
        choices=[],  # Empty choices initially
        required=False,
        widget=forms.Select(attrs={'class': 'category-field form-select'})
    )
    
    class Meta:
        model = Ticket
        fields = ['company', 'contact', 'priority', 'subject', 'description', 'category_type', 'category']

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        if self.initial.get('company'):
            self.fields['company'].widget.attrs['readonly'] = True

        # Dynamically set category choices based on category_type
        category_type = self.data.get('category_type') or self.initial.get('category_type')
        if category_type == 'client':
            self.fields['category'].choices = Ticket.CATEGORY_CHOICES_CLIENT
        elif category_type == 'agency':
            self.fields['category'].choices = Ticket.CATEGORY_CHOICES_AGENCY

        # Remove the 'disabled' attribute from the category field
        self.fields['category'].widget.attrs.pop('disabled', None)

    def clean_subject(self):
        subject_text = self.cleaned_data['subject']
        subject, _ = TicketSubject.objects.get_or_create(subject=subject_text)
        return subject