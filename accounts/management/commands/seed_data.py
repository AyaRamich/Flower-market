# accounts/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, SellerProfile, ClientProfile, DeliveryProfile, StockManagerProfile
from catalog.models import Category, FlowerStock, Bouquet, BouquetFlower
from orders.models import Order, OrderItem, Payment, Delivery
from messaging.models import Conversation, ConversationMessage, Notification
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de test réalistes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🌸 Démarrage du seeding...'))

        with transaction.atomic():
            self.create_categories()
            self.create_flower_stock()
            self.create_users()
            self.create_bouquets()
            self.create_orders()
            self.create_messages()

        self.stdout.write(self.style.SUCCESS('✅ Seeding terminé avec succès !'))
        self.stdout.write('')
        self.stdout.write('Comptes de test créés :')
        self.stdout.write('  Admin     → username: admin      | password: admin123')
        self.stdout.write('  Vendeur 1 → username: vendeur1   | password: test1234')
        self.stdout.write('  Vendeur 2 → username: vendeur2   | password: test1234')
        self.stdout.write('  Client 1  → username: client1    | password: test1234')
        self.stdout.write('  Client 2  → username: client2    | password: test1234')
        self.stdout.write('  Livreur   → username: livreur1   | password: test1234')
        self.stdout.write('  Stock     → username: stock1     | password: test1234')

    # ─── CATÉGORIES ─────────────────────────────────────────────────────────────

    def create_categories(self):
        self.stdout.write('  📁 Création des catégories...')

        categories = [
            'Romantique', 'Mariage', 'Anniversaire', 'Deuil',
            'Naissance', 'Fête des mères', 'Tropical', 'Sauvage',
        ]

        self.categories = []
        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name)
            self.categories.append(cat)

        self.stdout.write(f'     → {len(self.categories)} catégories créées')

    # ─── STOCK FLORAL ───────────────────────────────────────────────────────────

    def create_flower_stock(self):
        self.stdout.write('  🌿 Création du stock floral...')

        flowers_data = [
            {'flower_name': 'Rose Rouge',       'quantity': 500, 'unit': 'stem',  'min_threshold': 50},
            {'flower_name': 'Rose Blanche',     'quantity': 300, 'unit': 'stem',  'min_threshold': 30},
            {'flower_name': 'Rose Rose',        'quantity': 400, 'unit': 'stem',  'min_threshold': 40},
            {'flower_name': 'Tulipe',           'quantity': 250, 'unit': 'stem',  'min_threshold': 25},
            {'flower_name': 'Pivoine',          'quantity': 150, 'unit': 'stem',  'min_threshold': 20},
            {'flower_name': 'Lys Blanc',        'quantity': 200, 'unit': 'stem',  'min_threshold': 20},
            {'flower_name': 'Orchidée',         'quantity': 80,  'unit': 'pot',   'min_threshold': 10},
            {'flower_name': 'Tournesol',        'quantity': 180, 'unit': 'stem',  'min_threshold': 20},
            {'flower_name': 'Lavande',          'quantity': 120, 'unit': 'bunch', 'min_threshold': 15},
            {'flower_name': 'Jasmin',           'quantity': 90,  'unit': 'bunch', 'min_threshold': 10},
            {'flower_name': 'Mimosa',           'quantity': 60,  'unit': 'bunch', 'min_threshold': 8},
            {'flower_name': 'Gerbera',          'quantity': 200, 'unit': 'stem',  'min_threshold': 25},
            {'flower_name': 'Chrysanthème',     'quantity': 8,   'unit': 'stem',  'min_threshold': 20},  # stock faible
            {'flower_name': 'Marguerite',       'quantity': 0,   'unit': 'stem',  'min_threshold': 30},  # épuisé
        ]

        self.flowers = []
        for data in flowers_data:
            flower, _ = FlowerStock.objects.get_or_create(
                flower_name=data['flower_name'],
                defaults=data
            )
            self.flowers.append(flower)

        self.stdout.write(f'     → {len(self.flowers)} fleurs créées')

    # ─── UTILISATEURS ───────────────────────────────────────────────────────────

    def create_users(self):
        self.stdout.write('  👥 Création des utilisateurs...')

        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@floralshop.ma',
                password='admin123',
                role=User.Role.ADMIN,
                first_name='Admin',
                last_name='FloralShop',
                city='Casablanca',
            )
        else:
            admin = User.objects.get(username='admin')

       

        # Vendeurs
        vendors_data = [
            {
                'username': 'vendeur1',
                'email': 'vendeur1@floralshop.ma',
                'first_name': 'Fatima',
                'last_name': 'Benali',
                'city': 'Casablanca',
                'phone': '0661234567',
                'shop': {
                    'shop_name': 'Fleurs de Casablanca',
                    'description': 'Bouquets frais et élégants, créés avec passion depuis 2015.',
                    'city': 'Casablanca',
                    'address': '12 Rue Mohammed V, Casablanca',
                    'is_verified': True,
                }
            },
            {
                'username': 'vendeur2',
                'email': 'vendeur2@floralshop.ma',
                'first_name': 'Youssef',
                'last_name': 'Idrissi',
                'city': 'Rabat',
                'phone': '0662345678',
                'shop': {
                    'shop_name': 'Le Jardin de Rabat',
                    'description': 'Spécialiste des bouquets de mariage et événements.',
                    'city': 'Rabat',
                    'address': '5 Avenue Hassan II, Rabat',
                    'is_verified': True,
                }
            },
        ]

        self.sellers = []
        for vd in vendors_data:
            shop_data = vd.pop('shop')
            user, created = User.objects.get_or_create(
                username=vd['username'],
                defaults={**vd, 'role': User.Role.SELLER}
            )
            if created:
                user.set_password('test1234')
                user.save()
            profile, _ = SellerProfile.objects.get_or_create(user=user, defaults=shop_data)
            self.sellers.append(profile)

        # Clients
        clients_data = [
            {
                'username': 'client1',
                'email': 'client1@gmail.com',
                'first_name': 'Sara',
                'last_name': 'Moussaoui',
                'city': 'Casablanca',
                'phone': '0663456789',
                'address': '8 Rue des Fleurs, Casablanca',
            },
            {
                'username': 'client2',
                'email': 'client2@gmail.com',
                'first_name': 'Ahmed',
                'last_name': 'Tazi',
                'city': 'Rabat',
                'phone': '0664567890',
                'address': '3 Boulevard Mohammed VI, Rabat',
            },
        ]

        self.clients = []
        for cd in clients_data:
            address = cd.pop('address')
            user, created = User.objects.get_or_create(
                username=cd['username'],
                defaults={**cd, 'role': User.Role.CLIENT}
            )
            if created:
                user.set_password('test1234')
                user.save()
            profile, _ = ClientProfile.objects.get_or_create(
                user=user,
                defaults={'delivery_address': address, 'city': cd['city']}
            )
            self.clients.append(user)

        # Livreur
        livreur, created = User.objects.get_or_create(
            username='livreur1',
            defaults={
                'email': 'livreur1@floralshop.ma',
                'role': User.Role.DELIVERY,
                'first_name': 'Achraf',
                'last_name': 'Hajji',
                'city': 'Casablanca',
                'phone': '0665678901',
            }
        )
        if created:
            livreur.set_password('test1234')
            livreur.save()
        self.livreur, _ = DeliveryProfile.objects.get_or_create(
            user=livreur,
            defaults={'vehicle_type': 'Moto', 'current_city': 'Casablanca'}
        )

        self.stdout.write('     → 7 utilisateurs créés')

    # ─── BOUQUETS ───────────────────────────────────────────────────────────────

    def create_bouquets(self):
        self.stdout.write('  💐 Création des bouquets...')

        bouquets_data = [
            {
                'seller': self.sellers[0],
                'name': 'Bouquet Romantique Rouge',
                'description': 'Un bouquet de roses rouges envoûtant, parfait pour déclarer votre amour.',
                'price': Decimal('180.00'),
                'stock': 15,
                'city': 'Casablanca',
                'categories': [0, 0],  # index dans self.categories
                'flowers': [(0, 12), (4, 3)],  # (index fleur, quantité)
            },
            {
                'seller': self.sellers[0],
                'name': 'Bouquet Printemps Pastel',
                'description': 'Mélange délicat de tulipes et pivoines aux couleurs douces.',
                'price': Decimal('150.00'),
                'stock': 10,
                'city': 'Casablanca',
                'categories': [2],
                'flowers': [(3, 8), (4, 5), (11, 4)],
            },
            {
                'seller': self.sellers[0],
                'name': 'Composition Mariage Blanc',
                'description': 'Élégante composition blanche pour votre jour J.',
                'price': Decimal('350.00'),
                'stock': 5,
                'city': 'Casablanca',
                'categories': [1],
                'flowers': [(1, 20), (5, 10), (6, 3)],
            },
            {
                'seller': self.sellers[1],
                'name': 'Bouquet Tropical Exotique',
                'description': 'Couleurs vives et fleurs tropicales pour une ambiance estivale.',
                'price': Decimal('200.00'),
                'stock': 8,
                'city': 'Rabat',
                'categories': [6],
                'flowers': [(7, 6), (11, 8)],
            },
            {
                'seller': self.sellers[1],
                'name': 'Bouquet Fête des Mères',
                'description': 'Un hommage floral pour la femme de votre vie.',
                'price': Decimal('220.00'),
                'stock': 12,
                'city': 'Rabat',
                'categories': [5],
                'flowers': [(2, 10), (4, 5), (8, 3)],
            },
            {
                'seller': self.sellers[1],
                'name': 'Jardin Sauvage',
                'description': 'Fleurs des champs récoltées à l\'aube pour une touche nature.',
                'price': Decimal('120.00'),
                'stock': 20,
                'city': 'Rabat',
                'categories': [7],
                'flowers': [(9, 5), (10, 4), (11, 6)],
            },
        ]

        self.bouquets = []
        for bd in bouquets_data:
            cat_indices  = bd.pop('categories')
            flower_data  = bd.pop('flowers')

            bouquet, created = Bouquet.objects.get_or_create(
                name=bd['name'],
                seller=bd['seller'],
                defaults=bd
            )

            if created:
                # Catégories
                for idx in cat_indices:
                    bouquet.categories.add(self.categories[idx])

                # Fleurs utilisées
                for flower_idx, qty in flower_data:
                    BouquetFlower.objects.get_or_create(
                        bouquet=bouquet,
                        flower_stock=self.flowers[flower_idx],
                        defaults={'quantity': qty}
                    )

            self.bouquets.append(bouquet)

        self.stdout.write(f'     → {len(self.bouquets)} bouquets créés')

    # ─── COMMANDES ──────────────────────────────────────────────────────────────

    def create_orders(self):
        self.stdout.write('  📦 Création des commandes...')

        orders_data = [
            # Commande livrée
            {
                'client':          self.clients[0],
                'seller':          self.sellers[0],
                'bouquet':         self.bouquets[0],
                'quantity':        1,
                'total_price':     Decimal('180.00'),
                'status':          'delivered',
                'payment_method':  'on_delivery',
                'delivery_address': '8 Rue des Fleurs',
                'delivery_city':   'Casablanca',
                'payment_status':  'completed',
                'delivery_status': 'delivered',
            },
            # Commande en livraison
            {
                'client':          self.clients[0],
                'seller':          self.sellers[0],
                'bouquet':         self.bouquets[1],
                'quantity':        2,
                'total_price':     Decimal('300.00'),
                'status':          'shipped',
                'payment_method':  'transfer',
                'delivery_address': '8 Rue des Fleurs',
                'delivery_city':   'Casablanca',
                'payment_status':  'pending',
                'delivery_status': 'on_road',
            },
            # Commande en attente (vendeur doit accepter)
            {
                'client':          self.clients[1],
                'seller':          self.sellers[1],
                'bouquet':         self.bouquets[3],
                'quantity':        1,
                'total_price':     Decimal('200.00'),
                'status':          'pending',
                'payment_method':  'on_delivery',
                'delivery_address': '3 Boulevard Mohammed VI',
                'delivery_city':   'Rabat',
                'payment_status':  'pending',
                'delivery_status': None,
            },
            # Commande acceptée (livreur peut prendre)
            {
                'client':          self.clients[1],
                'seller':          self.sellers[0],
                'bouquet':         self.bouquets[2],
                'quantity':        1,
                'total_price':     Decimal('350.00'),
                'status':          'accepted',
                'payment_method':  'transfer',
                'delivery_address': '3 Boulevard Mohammed VI',
                'delivery_city':   'Rabat',
                'payment_status':  'pending',
                'delivery_status': 'waiting',
            },
        ]

        self.orders = []
        for od in orders_data:
            bouquet        = od.pop('bouquet')
            quantity       = od.pop('quantity')
            payment_status = od.pop('payment_status')
            delivery_status = od.pop('delivery_status')

            order, created = Order.objects.get_or_create(
                client=od['client'],
                seller=od['seller'],
                total_price=od['total_price'],
                defaults=od
            )

            if created:
                # Item
                OrderItem.objects.create(
                    order=order,
                    bouquet=bouquet,
                    quantity=quantity,
                    price=bouquet.price,
                )

                # Paiement
                Payment.objects.create(
                    order=order,
                    method=order.payment_method,
                    amount=order.total_price,
                    status=payment_status,
                )

                # Livraison
                if delivery_status:
                    Delivery.objects.create(
                        order=order,
                        delivery_person=self.livreur if delivery_status in ['on_road', 'delivered'] else None,
                        status=delivery_status,
                        pickup_address=order.seller.address,
                        dropoff_address=order.delivery_address,
                    )
                    if delivery_status in ['on_road', 'delivered']:
                        order.delivery_person = self.livreur
                        order.save()

            self.orders.append(order)

        self.stdout.write(f'     → {len(self.orders)} commandes créées')

 

   

        # Notifications
        Notification.objects.get_or_create(
            recipient=self.sellers[0].user,
            type='new_order',
            title='Nouvelle commande',
            defaults={
                'message': f'client1 a passé une commande de 180 MAD',
                'link': f'/orders/{self.orders[0].pk}/',
            }
        )

        Notification.objects.get_or_create(
            recipient=self.clients[0],
            type='order_accepted',
            title='Commande acceptée',
            defaults={
                'message': 'Fleurs de Casablanca a accepté votre commande !',
                'link': f'/orders/{self.orders[0].pk}/',
            }
        )

        self.stdout.write('     → conversations et notifications créées')