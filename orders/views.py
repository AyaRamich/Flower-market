# orders/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from catalog.models import Bouquet
from .models import Order, OrderItem, Payment, Delivery, StockUpdate
from accounts.models import DeliveryProfile
from accounts.dashboards import role_required


# CLIENT : PASSER UNE COMMANDE 

@role_required('client')
def order_create(request, bouquet_pk):
    bouquet = get_object_or_404(Bouquet, pk=bouquet_pk, status='available')

    if request.method == 'POST':
        quantity         = int(request.POST.get('quantity', 1))
        payment_method   = request.POST.get('payment_method', 'on_delivery')
        delivery_address = request.POST.get('delivery_address', '')
        delivery_city    = request.POST.get('delivery_city', '')
        note             = request.POST.get('note', '')

        # Vérifier stock suffisant
        if bouquet.stock < quantity:
            messages.error(request, f"Stock insuffisant. Disponible : {bouquet.stock}")
            return redirect('bouquet_detail', pk=bouquet_pk)

        total = bouquet.price * quantity

        # Créer la commande
        order = Order.objects.create(
            client=request.user,
            seller=bouquet.seller,
            total_price=total,
            payment_method=payment_method,
            delivery_address=delivery_address,
            delivery_city=delivery_city,
            note=note,
        )

        # Créer l'item
        OrderItem.objects.create(
            order=order,
            bouquet=bouquet,
            quantity=quantity,
            price=bouquet.price,
        )

        # Décrémenter le stock du bouquet
        bouquet.stock -= quantity
        bouquet.check_stock()  # met soldout si stock = 0

        # Créer le paiement en attente
        Payment.objects.create(
            order=order,
            method=payment_method,
            amount=total,
        )

        messages.success(request, "Commande passée avec succès ! Le vendeur va confirmer.")
        return redirect('order_detail', pk=order.pk)

    context = {'bouquet': bouquet}
    return render(request, 'orders/order_create.html', context)


#  CLIENT : MES COMMANDES 

@login_required
def order_list(request):
    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    # Client voit ses commandes, vendeur voit les siennes
    if request.user.is_client:
        order = get_object_or_404(Order, pk=pk, client=request.user)
    elif request.user.is_seller:
        order = get_object_or_404(Order, pk=pk, seller=request.user.seller_profile)
    else:
        order = get_object_or_404(Order, pk=pk)

    items    = order.items.select_related('bouquet').all()
    delivery = getattr(order, 'delivery_detail', None)
    payment  = getattr(order, 'payment', None)

    context = {
        'order':    order,
        'items':    items,
        'delivery': delivery,
        'payment':  payment,
    }
    return render(request, 'orders/order_detail.html', context)


#VENDEUR : ACCEPTER / REFUSER 
@role_required('seller')
def order_accept(request, pk):
    order = get_object_or_404(Order, pk=pk, seller=request.user.seller_profile)

    if request.method == 'POST':
        if order.status != 'pending':
            messages.error(request, "Cette commande ne peut plus être modifiée.")
            return redirect('seller_dashboard')

        order.status = 'accepted'  # string direct, pas Order.Status.ACCEPTED
        order.save()

        Delivery.objects.create(
            order=order,
            pickup_address=order.seller.address,
            dropoff_address=order.delivery_address,
        )

        messages.success(request, f"Commande #{order.id} acceptée !")
        return redirect('seller_dashboard')

    return redirect('seller_dashboard')

@role_required('seller')
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk, seller=request.user.seller_profile)

    if request.method == 'POST':
        if order.status not in ['pending', 'accepted']:
            messages.error(request, "Impossible d'annuler cette commande.")
            return redirect('seller_dashboard')

        order.status = 'canceled'
        order.save()

        for item in order.items.all():
            if item.bouquet:
                item.bouquet.stock += item.quantity
                item.bouquet.check_stock()

        if hasattr(order, 'payment'):
            order.payment.status = 'failed'
            order.payment.save()

        messages.success(request, f"Commande #{order.id} annulée.")
        return redirect('seller_dashboard')

    return redirect('seller_dashboard')

# ─── LIVREUR : ACCEPTER UNE LIVRAISON 
@role_required('delivery')
def delivery_accept(request, pk):
    order = get_object_or_404(Order, pk=pk, status='accepted')

    if request.method == 'POST':
        profile = request.user.delivery_profile

        # Vérifier que personne n'a déjà pris cette livraison
        if order.delivery_person is not None:
            messages.error(request, "Cette livraison a déjà été prise.")
            return redirect('delivery_dashboard')

        order.delivery_person = profile
        order.status          = 'preparing'
        order.save()

        # Mettre à jour ou créer la livraison
        delivery, _ = Delivery.objects.get_or_create(order=order)
        delivery.delivery_person = profile
        delivery.status          = 'preparing'
        delivery.accepted_at     = timezone.now()
        delivery.save()

        messages.success(request, f"Livraison #{order.id} acceptée !")
        return redirect('delivery_dashboard')

    return redirect('delivery_dashboard')

@role_required('delivery')
def delivery_update_status(request, pk):
    profile = request.user.delivery_profile
    order   = get_object_or_404(Order, pk=pk, delivery_person=profile)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        status_map = {
            'preparing': ('preparing', 'preparing'),
            'on_road':   ('on_road',   'shipped'),
            'delivered': ('delivered', 'delivered'),
        }

        if new_status not in status_map:
            messages.error(request, "Statut invalide.")
            return redirect('delivery_dashboard')

        d_status, o_status = status_map[new_status]

        # Mettre à jour la commande
        order.status = o_status
        order.save()

        
        delivery = Delivery.objects.filter(order=order).first()
        if delivery:
            delivery.status = d_status
            if new_status == 'delivered':
                delivery.delivered_at = timezone.now()
            delivery.save()

        # Si livré → confirmer paiement
        if new_status == 'delivered':
            try:
                
                if hasattr(order, 'payment') and order.payment:
                    order.payment.status  = 'completed'
                    order.payment.paid_at = timezone.now()
                    order.payment.save()
            except Exception:
                pass

            
            try:
                profile.total_deliveries += 1
                profile.save()
            except AttributeError:
               
                pass

        messages.success(request, "Statut mis à jour ✅")
        return redirect('delivery_dashboard')

    return redirect('delivery_dashboard')
# ─── ADMIN / STOCK : DASHBOARD COMMANDES

@login_required
def order_dashboard(request):
    if not (request.user.is_admin or request.user.is_seller):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    context = {
        'total_orders':   Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue':  Payment.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0,
        'recent_orders':  Order.objects.order_by('-created_at')[:10],
    }
    return render(request, 'orders/dashboard.html', context)


@role_required('seller')
def seller_order_detail(request, pk):
    order    = get_object_or_404(Order, pk=pk, seller=request.user.seller_profile)
    items    = order.items.select_related('bouquet').all()
    delivery = getattr(order, 'delivery_detail', None)
    payment  = getattr(order, 'payment', None)

    context = {
        'order':    order,
        'items':    items,
        'delivery': delivery,
        'payment':  payment,
    }
    return render(request, 'orders/seller_order_detail.html', context)