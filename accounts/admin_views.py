# accounts/admin_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count
from .dashboards import role_required
from .models import User, SellerProfile, DeliveryProfile
from catalog.models import FlowerStock, Category, Bouquet
from orders.models import Order, Payment


# ─── DASHBOARD PRINCIPAL 

@role_required('admin')
def admin_dashboard(request):
    section = request.GET.get('section', 'overview')

    context = {
        'section': section,
        # Overview
        'total_users':      User.objects.count(),
        'total_sellers':    User.objects.filter(role='seller').count(),
        'total_clients':    User.objects.filter(role='client').count(),
        'total_orders':     Order.objects.count(),
        'pending_orders':   Order.objects.filter(status='pending').count(),
        'total_revenue':    Payment.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0,
        'soldout_bouquets': Bouquet.objects.filter(status='soldout').count(),
        'low_stock':        FlowerStock.objects.filter(quantity__lte=10),
        # Users
        'users':      User.objects.all().order_by('-date_joined'),
        # Sellers
        'sellers':    SellerProfile.objects.select_related('user').all(),
        # Stock
        'flowers':    FlowerStock.objects.all().order_by('flower_name'),
        # Categories
        'categories': Category.objects.all(),
        # Orders
        'orders':     Order.objects.select_related('client', 'seller').order_by('-created_at'),
        'payment_stats': {
            'total':   Payment.objects.count(),
            'success': Payment.objects.filter(status='completed').count(),
            'failed':  Payment.objects.filter(status='failed').count(),
        },
        'recent_orders': Order.objects.order_by('-created_at')[:10],
    }
    return render(request, 'dashboards/admin.html', context)


# ─── GESTION UTILISATEURS 

@role_required('admin')
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


@role_required('admin')
def admin_user_toggle(request, pk):
    """Activer / désactiver un utilisateur."""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        status = "activé" if user.is_active else "désactivé"
        messages.success(request, f"Utilisateur {user.username} {status}.")
    return redirect('admin_users')


@role_required('admin')
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé.")
    return redirect('admin_users')


# ─── GESTION STOCK 

@role_required('admin')
def admin_stock(request):
    flowers = FlowerStock.objects.all().order_by('flower_name')
    return render(request, 'admin_panel/stock.html', {'flowers': flowers})


@role_required('admin')
def admin_stock_create(request):
    if request.method == 'POST':
        FlowerStock.objects.create(
            flower_name   = request.POST.get('flower_name'),
            description   = request.POST.get('description', ''),
            quantity      = request.POST.get('quantity', 0),
            unit          = request.POST.get('unit', 'stem'),
            min_threshold = request.POST.get('min_threshold', 10),
        )
        messages.success(request, "Fleur ajoutée au stock.")
        return redirect('admin_stock')
    return render(request, 'admin_panel/stock_form.html', {'flower': None})


@role_required('admin')
def admin_stock_edit(request, pk):
    flower = get_object_or_404(FlowerStock, pk=pk)
    if request.method == 'POST':
        flower.flower_name   = request.POST.get('flower_name', flower.flower_name)
        flower.quantity      = request.POST.get('quantity', flower.quantity)
        flower.unit          = request.POST.get('unit', flower.unit)
        flower.min_threshold = request.POST.get('min_threshold', flower.min_threshold)
        flower.description   = request.POST.get('description', flower.description)
        flower.save()
        messages.success(request, "Stock mis à jour.")
        return redirect('admin_stock')
    return render(request, 'admin_panel/stock_form.html', {'flower': flower})


@role_required('admin')
def admin_stock_delete(request, pk):
    flower = get_object_or_404(FlowerStock, pk=pk)
    if request.method == 'POST':
        flower.delete()
        messages.success(request, "Fleur supprimée.")
    return redirect('admin_stock')


# ─── GESTION CATÉGORIES 

@role_required('admin')
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'admin_panel/categories.html', {'categories': categories})


@role_required('admin')
def admin_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, f"Catégorie '{name}' créée.")
    return redirect('admin_categories')


@role_required('admin')
def admin_category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, "Catégorie supprimée.")
    return redirect('admin_categories')


# ─── GESTION VENDEURS 

@role_required('admin')
def admin_sellers(request):
    sellers = SellerProfile.objects.select_related('user').all()
    return render(request, 'admin_panel/sellers.html', {'sellers': sellers})


@role_required('admin')
def admin_seller_verify(request, pk):
    seller = get_object_or_404(SellerProfile, pk=pk)
    if request.method == 'POST':
        seller.is_verified = not seller.is_verified
        seller.save()
        status = "vérifié" if seller.is_verified else "non vérifié"
        messages.success(request, f"{seller.shop_name} marqué {status}.")
    return redirect('admin_sellers')


# ─── TOUTES LES COMMANDES 

@role_required('admin')
def admin_order_detail(request, pk):
    order    = get_object_or_404(Order, pk=pk)
    items    = order.items.select_related('bouquet').all()
    delivery = getattr(order, 'delivery_detail', None)
    payment  = getattr(order, 'payment', None)
    context  = {
        'order':    order,
        'items':    items,
        'delivery': delivery,
        'payment':  payment,
    }
    return render(request, 'orders/order_detail.html', context)
@role_required('admin')
def admin_orders(request):
    orders = Order.objects.select_related('client', 'seller').order_by('-created_at')
    context = {
        'orders': orders,
        'payment_stats': {
            'total':   Payment.objects.count(),
            'success': Payment.objects.filter(status='completed').count(),
            'failed':  Payment.objects.filter(status='failed').count(),
        }
    }
    return render(request, 'admin_panel/orders.html', context)
