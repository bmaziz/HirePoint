from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations complémentaires', {'fields': ('role', 'dateInscription')}),
    )
    readonly_fields = ('dateInscription',)
    list_display = ('username', 'email', 'role', 'dateInscription', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
