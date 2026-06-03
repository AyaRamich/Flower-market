# orders/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.order_list,             name='order_list'),
    path('<int:pk>/',                     views.order_detail,           name='order_detail'),
    path('create/<int:bouquet_pk>/',      views.order_create,           name='order_create'),
    path('<int:pk>/accept/',              views.order_accept,           name='order_accept'),
    path('<int:pk>/cancel/',              views.order_cancel,           name='order_cancel'),
    path('<int:pk>/delivery/accept/',     views.delivery_accept,        name='delivery_accept'),
    path('<int:pk>/delivery/status/',     views.delivery_update_status, name='delivery_update_status'),
    path('dashboard/',                    views.order_dashboard,        name='order_dashboard'),
    path('seller/<int:pk>/', views.seller_order_detail, name='seller_order_detail'),
]