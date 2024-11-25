# agencies/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Agency

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'agency']
    list_filter = ['user_type', 'agency']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'agency')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'agency')}),
    )

class AgencyAdmin(admin.ModelAdmin):
    list_display = ['agency_name', 'email', 'phone', 'vat_number', 'company_reg_number', 'business_focus', 'employees', 'created_at']
    list_filter = ['business_focus', 'employees']
    search_fields = ['agency_name', 'email', 'vat_number', 'company_reg_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {'fields': ('name', 'email', 'phone', 'website')}),
        ('Company Details', {'fields': ('vat_number', 'company_reg_number', 'business_focus', 'employees')}),
        ('Address', {'fields': ('address',)}),
        ('Contact', {'fields': ('contact_name',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Agency, AgencyAdmin)