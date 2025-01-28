from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Candidate, User

# Customize the Candidate admin view
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('c_first_name', 'c_last_name', 'c_email', 'c_skills', 'c_registration_date', 'age')
    search_fields = ('c_first_name', 'c_last_name', 'c_email')
    list_filter = ('c_registration_date',)
    ordering = ('-c_registration_date',)

# Customize the User admin view
class CustomUserAdmin(UserAdmin):
    # Define the fields to be shown in the user list page
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    ordering = ('-date_joined',)
    
    # Define the fields to be shown in the user detail page
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    exclude = ('first_name', 'last_name')

    # Define the fields for adding a new user (superuser)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

# Register the Candidate model with custom admin view
admin.site.register(Candidate, CandidateAdmin)

# Register the User model with custom admin view
admin.site.register(User, CustomUserAdmin)
