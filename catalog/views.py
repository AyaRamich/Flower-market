# catalog/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Bouquet, Category, FlowerStock, BouquetImage, BouquetFlower
from accounts.models import SellerProfile
from accounts.dashboards import role_required

from catalog import models
from .models import Review
from orders.models import Order


# HOMEPAGE 

def home(request):
    bouquets   = Bouquet.objects.filter(status='available').order_by('-created_at')
    categories = Category.objects.all()

    # Filtres
    q         = request.GET.get('q', '')
    category  = request.GET.get('category', '')
    city      = request.GET.get('city', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if q:
        bouquets = bouquets.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )
    if category:
        bouquets = bouquets.filter(categories__slug=category)
    if city:
        bouquets = bouquets.filter(city__icontains=city)
    if min_price:
        bouquets = bouquets.filter(price__gte=min_price)
    if max_price:
        bouquets = bouquets.filter(price__lte=max_price)

    context = {
        'bouquets':   bouquets,
        'categories': categories,
        'q':          q,
        'city':       city,
    }
    return render(request, 'home.html', context)


# ─── DETAIL BOUQUET

def bouquet_detail(request, pk):
    bouquet = get_object_or_404(Bouquet, pk=pk)
    images  = bouquet.images.all()
    flowers = BouquetFlower.objects.filter(bouquet=bouquet).select_related('flower_stock')

    context = {
        'bouquet': bouquet,
        'images':  images,
        'flowers': flowers,
    }
    return render(request, 'catalog/bouquet_detail.html', context)


# ─── PROFIL VENDEUR PUBLIC 

def seller_public_profile(request, pk):
    seller   = get_object_or_404(SellerProfile, pk=pk)
    bouquets = Bouquet.objects.filter(seller=seller, status='available')

    context = {
        'seller':   seller,
        'bouquets': bouquets,
    }
    return render(request, 'catalog/seller_profile.html', context)


# ─── VUES VENDEUR : GÉRER SES BOUQUETS 
@role_required('seller')
def seller_bouquet_list(request):
    profile  = request.user.seller_profile
    bouquets = Bouquet.objects.filter(seller=profile).order_by('-created_at')
    return render(request, 'catalog/seller_bouquets.html', {'bouquets': bouquets})


@role_required('seller')
def bouquet_create(request):
    categories = Category.objects.all()
    flowers    = FlowerStock.objects.filter(quantity__gt=0)

    if request.method == 'POST':
        name        = request.POST.get('name')
        description = request.POST.get('description')
        price       = request.POST.get('price')
        stock       = request.POST.get('stock')
        city        = request.POST.get('city')
        cat_ids     = request.POST.getlist('categories')
        flower_ids  = request.POST.getlist('flowers')
        quantities  = request.POST.getlist('flower_quantities')

        profile = request.user.seller_profile
        bouquet = Bouquet.objects.create(
            seller=profile,
            name=name,
            description=description,
            price=price,
            stock=stock,
            city=city,
        )

        
        bouquet.categories.set(cat_ids)

       
        for flower_id, qty in zip(flower_ids, quantities):
            if flower_id and qty:
                BouquetFlower.objects.create(
                    bouquet=bouquet,
                    flower_stock_id=flower_id,
                    quantity=int(qty)
                )

        # Ajouter images
        for img in request.FILES.getlist('images'):
            BouquetImage.objects.create(bouquet=bouquet, image=img)

        messages.success(request, "Bouquet créé avec succès !")
        return redirect('seller_bouquet_list')

    context = {'categories': categories, 'flowers': flowers}
    return render(request, 'catalog/bouquet_form.html', context)


@role_required('seller')
def bouquet_edit(request, pk):
    profile = request.user.seller_profile
    bouquet = get_object_or_404(Bouquet, pk=pk, seller=profile)
    categories = Category.objects.all()
    flowers = FlowerStock.objects.filter(quantity__gt=0)

    if request.method == 'POST':
        bouquet.name        = request.POST.get('name', bouquet.name)
        bouquet.description = request.POST.get('description', bouquet.description)
        bouquet.price       = request.POST.get('price', bouquet.price)
        bouquet.stock       = request.POST.get('stock', bouquet.stock)
        bouquet.city        = request.POST.get('city', bouquet.city)
        cat_ids             = request.POST.getlist('categories')
        bouquet.categories.set(cat_ids)

        for img in request.FILES.getlist('images'):
            BouquetImage.objects.create(bouquet=bouquet, image=img)

        bouquet.check_stock()  # met à jour soldout automatiquement
        bouquet.save()

        messages.success(request, "Bouquet mis à jour !")
        return redirect('seller_bouquet_list')

    context = {'bouquet': bouquet, 'categories': categories, 'flowers': flowers}
    return render(request, 'catalog/bouquet_form.html', context)


@role_required('seller')
def bouquet_delete(request, pk):
    profile = request.user.seller_profile
    bouquet = get_object_or_404(Bouquet, pk=pk, seller=profile)

    if request.method == 'POST':
        bouquet.delete()
        messages.success(request, "Bouquet supprimé.")
        return redirect('seller_bouquet_list')

    return render(request, 'catalog/bouquet_confirm_delete.html', {'bouquet': bouquet})


 

@login_required
def stock_list(request):
    if not (request.user.is_admin or request.user.is_seller):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    flowers = FlowerStock.objects.all().order_by('flower_name')
    return render(request, 'catalog/stock_list.html', {'flowers': flowers})



def seller_public_profile(request, pk):
   
    seller   = get_object_or_404(SellerProfile, pk=pk)
    bouquets = Bouquet.objects.filter(seller=seller, status='available')
    reviews  = Review.objects.filter(seller=seller).select_related('client').order_by('-created_at')

    
    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0

   
    can_review = False
    existing_review = None
    if request.user.is_authenticated and request.user.is_client:
        delivered_order = Order.objects.filter(
            client=request.user,
            seller=seller,
            status='delivered'
        ).exclude(review__isnull=False).first()
        can_review = delivered_order is not None
        existing_review = Review.objects.filter(
            client=request.user,
            seller=seller
        ).first()

    context = {
        'seller':          seller,
        'bouquets':        bouquets,
        'reviews':         reviews,
        'avg_rating':      round(avg_rating, 1),
        'review_count':    reviews.count(),
        'can_review':      can_review,
        'existing_review': existing_review,
        'rating_range':    range(1, 6),
    }
    return render(request, 'catalog/seller_profile.html', context)


@role_required('client')
def submit_review(request, seller_pk):
    """Soumettre un avis sur un vendeur."""
    seller = get_object_or_404(SellerProfile, pk=seller_pk)

    if request.method == 'POST':
        rating  = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        # Trouver la commande livrée sans avis
        order = Order.objects.filter(
            client=request.user,
            seller=seller,
            status='delivered'
        ).exclude(review__isnull=False).first()

        if not order:
            messages.error(request, "Vous ne pouvez pas laisser d'avis pour ce vendeur.")
            return redirect('seller_profile', pk=seller_pk)

        if not (1 <= rating <= 5):
            messages.error(request, "Note invalide.")
            return redirect('seller_profile', pk=seller_pk)

        Review.objects.create(
            seller=seller,
            client=request.user,
            order=order,
            rating=rating,
            comment=comment,
        )

       
        avg = Review.objects.filter(seller=seller).aggregate(
            avg=models.Avg('rating')
        )['avg'] or 0
        seller.rating = round(avg, 2)
        seller.save()

        messages.success(request, "Merci pour votre avis ! 🌸")

    return redirect('seller_profile', pk=seller_pk)