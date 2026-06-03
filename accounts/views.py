# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, SellerProfile, ClientProfile, DeliveryProfile


#INSCRIPTION 

def register(request):
    if request.method == 'POST':
        username  = request.POST.get('username')
        email     = request.POST.get('email')
        password  = request.POST.get('password')
        role      = request.POST.get('role', User.Role.CLIENT)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'accounts/register.html')

        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
        )

        
        if role == User.Role.SELLER:
            shop_name = request.POST.get('shop_name', f"Boutique de {username}")
            SellerProfile.objects.create(user=user, shop_name=shop_name)

        elif role == User.Role.CLIENT:
            ClientProfile.objects.create(user=user)

        elif role == User.Role.DELIVERY:
            DeliveryProfile.objects.create(user=user)

       

        # Connexion automatique après inscription
        login(request, user)
        messages.success(request, f"Bienvenue {username} !")
        return redirect('dashboard')

    return render(request, 'accounts/register.html')


# CONNEXION 

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirection vers la page demandée avant le login, sinon dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'accounts/login.html')


#logout

def logout_view(request):
    logout(request)
    return redirect('login')


# ─── DASHBOARD (redirige selon le rôle) 

@login_required
def dashboard(request):
    user = request.user

    if user.is_admin:
        return redirect('admin_dashboard')
    elif user.is_seller:
        return redirect('seller_dashboard')
    elif user.is_client:
        return redirect('client_dashboard')
    elif user.is_delivery:
        return redirect('delivery_dashboard')
    

    return redirect('home')


# ─── PROFIL 
@login_required
def profile(request):
    user = request.user
    context = {'user': user}

    if user.is_seller:
        context['profile'] = SellerProfile.objects.filter(user=user).first()
   
    elif user.is_delivery:
        context['profile'] = DeliveryProfile.objects.filter(user=user).first()
    elif user.is_client:
        context['profile'] = ClientProfile.objects.filter(user=user).first()

    return render(request, 'accounts/profile.html', context)


# MODIFIER PROFIL 
@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        # Champs communs
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name  = request.POST.get('last_name', user.last_name)
        user.phone      = request.POST.get('phone', user.phone)
        user.city       = request.POST.get('city', user.city)

        if request.FILES.get('photo'):
            user.photo = request.FILES['photo']

        user.save()

        # Champs spécifiques au vendeur
        if user.is_seller:
            profile = SellerProfile.objects.filter(user=user).first()
            if profile:
                profile.shop_name   = request.POST.get('shop_name', profile.shop_name)
                profile.description = request.POST.get('description', profile.description)
                profile.address     = request.POST.get('address', profile.address)
                profile.city        = request.POST.get('city', profile.city)
                if request.FILES.get('banner'):
                    profile.banner = request.FILES['banner']
                profile.save()

        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('profile')

    # Préparer le contexte pour le formulaire
    context = {'user': user}
    if user.is_seller:
        context['profile'] = SellerProfile.objects.filter(user=user).first()

    return render(request, 'accounts/edit_profile.html', context)