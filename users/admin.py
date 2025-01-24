# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'rol', 'rut', 'direccion')}),
        ('Info Dueño', {'fields': ('cuenta_bancaria',)}),
        ('Info Cliente', {'fields': ('tarjeta_credito', 'banco',)}),
        ('Permisos Django', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'rol', 'rut', 'direccion',
                'cuenta_bancaria', 'tarjeta_credito', 'banco',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
    )
    list_display = ('username', 'rol', 'is_active', 'is_staff', 'is_superuser')
