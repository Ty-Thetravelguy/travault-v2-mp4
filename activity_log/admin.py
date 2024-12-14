# activity_log/admin.py
from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Meeting model.
    This class customizes the admin interface for managing meetings,
    including the fields displayed and the filtering options.
    """
    list_display = ('subject', 'date', 'time', 'company', 'creator')
    filter_horizontal = ('contacts', 'users') 
