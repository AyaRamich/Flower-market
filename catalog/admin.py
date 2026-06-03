from django.contrib import admin

# Register your models here.
# catalog/admin.py

from django.contrib import admin
from .models import Category, FlowerStock, Bouquet, BouquetImage, BouquetFlower


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class BouquetImageInline(admin.TabularInline):
    model = BouquetImage
    extra = 3


class BouquetFlowerInline(admin.TabularInline):
    model = BouquetFlower
    extra = 2


@admin.register(FlowerStock)
class FlowerStockAdmin(admin.ModelAdmin):
    list_display  = ['flower_name', 'quantity', 'unit', 'min_threshold', 'is_low_stock']
    list_editable = ['quantity']
    list_filter   = ['unit']
    search_fields = ['flower_name']


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display  = ['name', 'seller', 'price', 'stock', 'status', 'city']
    list_filter   = ['status', 'city']
    search_fields = ['name']
    inlines       = [BouquetImageInline, BouquetFlowerInline]