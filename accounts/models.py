

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN    = 'admin',    _('Administrateur')
        CLIENT   = 'client',   _('Client')
        SELLER   = 'seller',   _('Vendeur')
       
        DELIVERY = 'delivery', _('Livreur')

    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    city  = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT
    
    
   

    @property
    def is_delivery(self):
        return self.role == self.Role.DELIVERY

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class SellerProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    shop_name   = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    banner      = models.ImageField(upload_to='sellers/banners/', blank=True, null=True)
    address     = models.CharField(max_length=300, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    rating      = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name


class ClientProfile(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    delivery_address = models.CharField(max_length=300, blank=True)
    city             = models.CharField(max_length=100, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Client: {self.user.username}"


class DeliveryProfile(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    vehicle_type     = models.CharField(max_length=50, blank=True)
    is_available     = models.BooleanField(default=True)
    current_city     = models.CharField(max_length=100, blank=True)
    total_deliveries = models.PositiveIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Livreur: {self.user.username}"

