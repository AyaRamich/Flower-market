# accounts/urls.py

from django.urls import path

from . import dashboards
from . import views
from . import admin_views

urlpatterns = [
    path('register/',     views.register,     name='register'),
    path('login/',        views.login_view,   name='login'),
    path('logout/',       views.logout_view,  name='logout'),
    path('dashboard/',    views.dashboard,    name='dashboard'),
    path('profile/',      views.profile,      name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
     # Dashboards
    path('seller/dashboard/',   dashboards.seller_dashboard,   name='seller_dashboard'),
    path('client/dashboard/',   dashboards.client_dashboard,   name='client_dashboard'),
    path('delivery/dashboard/', dashboards.delivery_dashboard, name='delivery_dashboard'),
    
    #admin 
    path('panel/',                          admin_views.admin_dashboard,      name='admin_dashboard'),
    path('panel/users/',                    admin_views.admin_users,           name='admin_users'),
    path('panel/users/<int:pk>/toggle/',    admin_views.admin_user_toggle,     name='admin_user_toggle'),
    path('panel/users/<int:pk>/delete/',    admin_views.admin_user_delete,     name='admin_user_delete'),
    path('panel/stock/',                    admin_views.admin_stock,           name='admin_stock'),
    path('panel/stock/create/',             admin_views.admin_stock_create,    name='admin_stock_create'),
    path('panel/stock/<int:pk>/edit/',      admin_views.admin_stock_edit,      name='admin_stock_edit'),
    path('panel/stock/<int:pk>/delete/',    admin_views.admin_stock_delete,    name='admin_stock_delete'),
    path('panel/categories/',              admin_views.admin_categories,      name='admin_categories'),
    path('panel/categories/create/',       admin_views.admin_category_create, name='admin_category_create'),
    path('panel/categories/<int:pk>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),
    path('panel/sellers/',                  admin_views.admin_sellers,         name='admin_sellers'),
    path('panel/sellers/<int:pk>/verify/',  admin_views.admin_seller_verify,   name='admin_seller_verify'),
    path('panel/orders/',                   admin_views.admin_orders,          name='admin_orders'),
    path('panel/orders/<int:pk>/',          admin_views.admin_order_detail,    name='admin_order_detail'),

]