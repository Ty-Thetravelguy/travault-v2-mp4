# activity_log/admin.py
from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date', 'time', 'company', 'creator')
    filter_horizontal = ('contacts', 'users') 
