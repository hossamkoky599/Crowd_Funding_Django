from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailActivation, PasswordReset

class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'mobile_phone', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile_phone', 'profile_picture')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailActivation)
admin.site.register(PasswordReset)