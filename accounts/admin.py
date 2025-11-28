from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import *
# Register your models here.


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    ordering = ['phone']
    add_form = AppUserChangeForm
    form = AppUserChangeForm
    model = AppUser
    list_display = ['phone', 'first_name', 'last_name', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', )}),
    )

    add_fieldsets = (
        (None, {'fields': ('phone', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )

@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    fields = ['user', 'code', 'expire_at']
    ordering = ['created_at']

