from django import forms
from .models import ActivityLog

class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['activity_type', 'subject', 'description', 'related_contact']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }