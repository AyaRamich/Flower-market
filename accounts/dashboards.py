# accounts/dashboards.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from catalog.models import Bouquet, FlowerStock
from orders.models import Order, Payment
from .models import User, SellerProfile, DeliveryProfile


def role_required(role):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Accès refusé.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ADMIN DASHBOARD 

@role_required('admin')
def admin_dashboard(request):
    context = {
        'total_users':    User.objects.count(),
        'total_sellers':  User.objects.filter(role='seller').count(),
        'total_clients':  User.objects.filter(role='client').count(),
        'total_orders':   Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue':  Payment.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0,
        'low_stock':      FlowerStock.objects.filter(quantity__lte=10),
        'recent_orders':  Order.objects.order_by('-created_at')[:10],
        'soldout_bouquets': Bouquet.objects.filter(status='soldout').count(),
    }
    return render(request, 'dashboards/admin.html', context)


# SELLER DASHBOARD 

@role_required('seller')
def seller_dashboard(request):
    profile  = request.user.seller_profile
    bouquets = Bouquet.objects.filter(seller=profile)
    orders   = Order.objects.filter(seller=profile).order_by('-created_at')

    context = {
        'profile':          profile,
        'bouquets':         bouquets,
        'total_bouquets':   bouquets.count(),
        'active_bouquets':  bouquets.filter(status='available').count(),
        'soldout_bouquets': bouquets.filter(status='soldout').count(),
        'total_orders':     orders.count(),
        'pending_orders':   orders.filter(status='pending'),
        'recent_orders':    orders[:8],
        'total_revenue':    Payment.objects.filter(
                                order__seller=profile,
                                status='completed'
                            ).aggregate(t=Sum('amount'))['t'] or 0,
    }
    return render(request, 'dashboards/seller.html', context)


#CLIENT DASHBOARD 

@role_required('client')
def client_dashboard(request):
    orders = Order.objects.filter(client=request.user).order_by('-created_at')

    context = {
        'orders':           orders[:10],
        'total_orders':     orders.count(),
        'active_orders':    orders.exclude(status__in=['delivered', 'canceled']),
        'delivered_orders': orders.filter(status='delivered').count(),
    }
    return render(request, 'dashboards/client.html', context)


# ─── DELIVERY DASHBOARD 

@role_required('delivery')
def delivery_dashboard(request):
    profile = request.user.delivery_profile

    available_deliveries = Order.objects.filter(
        status='accepted',
        delivery_person=None
    ).select_related('seller', 'client')

    my_deliveries = Order.objects.filter(
        delivery_person=profile
    ).select_related('client', 'seller').order_by('-created_at')

    context = {
        'profile':              profile,
        'available_deliveries': available_deliveries,
        'active_deliveries':    my_deliveries.filter(status__in=['preparing', 'shipped']),
        'completed_deliveries': my_deliveries.filter(status='delivered').count(),
        'completed_orders':     my_deliveries.filter(status='delivered')[:10],
        'total_deliveries':     my_deliveries.count(),
    }
    return render(request, 'dashboards/delivery.html', context)

