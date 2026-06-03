# catalog/models.py

from django.db import models
from django.utils.text import slugify
from accounts.models import User, SellerProfile


class Category(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    slug  = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class FlowerStock(models.Model):
    

    class Unit(models.TextChoices):
        STEM   = 'stem',   'Tige'
        BUNCH  = 'bunch',  'Bouquet'
        POT    = 'pot',    'Pot'
        KG     = 'kg',     'Kilogramme'

   
    flower_name   = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    quantity      = models.PositiveIntegerField(default=0)
    unit          = models.CharField(max_length=10, choices=Unit.choices, default=Unit.STEM)
    min_threshold = models.PositiveIntegerField(default=10)  
    image         = models.ImageField(upload_to='flowers/', blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_threshold

    def __str__(self):
        return f"{self.flower_name} ({self.quantity} {self.unit})"


class Bouquet(models.Model):
    

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponible'
        SOLDOUT   = 'soldout',   'Épuisé'
        HIDDEN    = 'hidden',    'Masqué'

    seller      = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='bouquets')
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    city        = models.CharField(max_length=100, blank=True)
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    categories  = models.ManyToManyField(Category, related_name='bouquets', blank=True)
    flowers     = models.ManyToManyField(FlowerStock, through='BouquetFlower', related_name='used_in', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def check_stock(self):
       
        if self.stock == 0:
            self.status = self.Status.SOLDOUT
        elif self.status == self.Status.SOLDOUT:
            self.status = self.Status.AVAILABLE
        self.save()

    def __str__(self):
        return f"{self.name} - {self.seller.shop_name}"


class BouquetFlower(models.Model):
   
    bouquet      = models.ForeignKey(Bouquet, on_delete=models.CASCADE)
    flower_stock = models.ForeignKey(FlowerStock, on_delete=models.CASCADE)
    quantity     = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('bouquet', 'flower_stock')

    def __str__(self):
        return f"{self.quantity}x {self.flower_stock.flower_name} dans {self.bouquet.name}"


class BouquetImage(models.Model):
   
    bouquet  = models.ForeignKey(Bouquet, on_delete=models.CASCADE, related_name='images')
    image    = models.ImageField(upload_to='bouquets/')
    is_cover = models.BooleanField(default=False)  # image principale

    def __str__(self):
        return f"Image de {self.bouquet.name}"
    
class Review(models.Model):
    """Avis client sur un vendeur après livraison."""
    seller    = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='reviews')
    client    = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews')
    order     = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='review')
    rating    = models.PositiveSmallIntegerField()  # 1 à 5
    comment   = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seller', 'client', 'order')

    def __str__(self):
        return f"{self.client.username} → {self.seller.shop_name} ({self.rating}⭐)"