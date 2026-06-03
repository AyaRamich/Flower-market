# catalog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('',                          views.home,                  name='home'),
    path('bouquet/<int:pk>/',         views.bouquet_detail,        name='bouquet_detail'),
    path('seller/<int:pk>/',          views.seller_public_profile, name='seller_profile'),

    # Vendeur
    path('my-bouquets/',              views.seller_bouquet_list,   name='seller_bouquet_list'),
    path('my-bouquets/create/',       views.bouquet_create,        name='bouquet_create'),
    path('my-bouquets/<int:pk>/edit/', views.bouquet_edit,         name='bouquet_edit'),
    path('my-bouquets/<int:pk>/delete/', views.bouquet_delete,     name='bouquet_delete'),

    # Stock
    path('stock/',                    views.stock_list,            name='stock_list'),
]