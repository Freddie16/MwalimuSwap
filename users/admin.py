# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom Admin configuration for the CustomUser model.
    Uses CustomUserCreationForm for adding users and CustomUserChangeForm for changing users.
    Defines fieldsets for better organization in the admin interface.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        'username', 'email', 'full_name', 'phone_number',
        'is_staff', 'is_profile_complete'
    ]
    list_filter = ['is_staff', 'is_active', 'is_profile_complete', 'school_type', 'current_county']
    search_fields = ['username', 'email', 'full_name', 'phone_number']
    ordering = ['username']

    # Fieldsets for editing an existing user
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_name', 'phone_number', 'profile_picture', 'is_profile_complete')}),
        ('School Information', {'fields': ('school_type', 'subjects')}),
        ('Current Location', {'fields': ('current_county', 'current_subcounty', 'current_ward')}),
        ('Swap To Location', {'fields': ('swap_to_county', 'swap_to_subcounty', 'swap_to_ward')}),
    )
    # Fieldsets for adding a new user (simplified)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('full_name', 'phone_number', 'email')}),
    )
