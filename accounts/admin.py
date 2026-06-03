from django.contrib import admin

# Register your models here.
# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SellerProfile, ClientProfile, DeliveryProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_active']
    search_fields = ['username', 'email']
    fieldsets     = UserAdmin.fieldsets + (
        ('Rôle & Infos', {'fields': ('role', 'phone', 'city', 'photo')}),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'user', 'city', 'is_verified', 'rating']
    list_editable = ['is_verified']


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city']


@admin.register(DeliveryProfile)
class DeliveryProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_available', 'current_city', 'total_deliveries']
    list_editable = ['is_available']