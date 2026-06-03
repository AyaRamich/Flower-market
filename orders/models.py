from django.db import models
from catalog.models import Bouquet,FlowerStock
from accounts.models import User, SellerProfile, DeliveryProfile

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'En attente'
        CONFIRMED = 'confirmed', 'Confirmée'
        
        SHIPPED   = 'shipped',   'Expédiée'
        DELIVERED = 'delivered', 'Livrée'
        CANCELED  = 'canceled',  'Annulée'
    class PaymentMethod(models.TextChoices):
        
        ON_DELIVERY='on_delivery','à la livraison'


    client       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller       = models.ForeignKey(SellerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    delivery_person     = models.ForeignKey(DeliveryProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    total_price  = models.DecimalField(max_digits=10, decimal_places=2)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_method  = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.ON_DELIVERY)
    delivery_address = models.CharField(max_length=300, blank=True)
    delivery_city   = models.CharField(max_length=100, blank=True)
    note            = models.TextField(blank=True)  
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.client.username} - {self.get_status_display()}"

class OrderItem(models.Model):
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    bouquet      = models.ForeignKey(Bouquet, on_delete=models.SET_NULL, null=True)
    quantity     = models.PositiveIntegerField(default=1)
    price        = models.DecimalField(max_digits=10, decimal_places=2)


    def get_subtotal(self):
        return self.quantity*self.price
    
    def __str__(self):
        return f"{self.quantity} x {self.bouquet.name} for Order #{self.order.id}"
    



class Delivery(models.Model):
    class Status(models.TextChoices):
        WAITING   = 'waiting',   'En attente'
        PREPARING = 'preparing', 'En préparation'
        ON_ROAD   = 'on_road',   'En livraison'
        DELIVERED = 'delivered', 'Livrée'

    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='delivery')
    delivery_person=models.ForeignKey(DeliveryProfile,on_delete=models.SET_NULL,null=True,blank=True,related_name='livreur')
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.WAITING)
    pickup_address  = models.CharField(max_length=300, blank=True)   # adresse vendeur
    dropoff_address = models.CharField(max_length=300, blank=True)   # adresse client
    accepted_at     = models.DateTimeField(null=True, blank=True)
    delivered_at    = models.DateTimeField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Livraison Order #{self.order.id} — {self.get_status_display()}"

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'En attente'
        COMPLETED = 'completed', 'Complété'
        FAILED    = 'failed',    'Échoué'
        
    order=models.OneToOneField(Order,on_delete=models.CASCADE,related_name='payment')
    method=models.CharField(max_length=20,choices=Order.PaymentMethod.choices)
    amount    = models.DecimalField(max_digits=10, decimal_places=2)
    status    = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Paiement Order #{self.order.id} — {self.amount} MAD"
class StockUpdate(models.Model):
    

    class Action(models.TextChoices):
        ADD    = 'add',    'Ajout'
        REMOVE = 'remove', 'Retrait'
        ADJUST = 'adjust', 'Ajustement'

    stock_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_updates')
    flower_stock  = models.ForeignKey(FlowerStock, on_delete=models.CASCADE, related_name='updates')
    action        = models.CharField(max_length=10, choices=Action.choices)
    quantity      = models.IntegerField()
    note          = models.CharField(max_length=200, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_display()} {self.quantity} — {self.flower_stock.flower_name}"