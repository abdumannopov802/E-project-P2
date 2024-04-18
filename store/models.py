from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
    
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
 
    def __str__(self):
        return self.name
 
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expire_date = models.DateField()
 
    def __str__(self):
        return self.name

class ShopCard(models.Model):
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100)
 
    def __str__(self):
        return str(self.id)
 
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey(ShopCard, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return str(self.cart)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class PurchaseHistory(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateField(auto_now_add=True)


############################

# class ShopCard(models.Model):
#     customer = models.OneToOneField(Customer, related_name='shop_card', on_delete=models.CASCADE)

# class Item(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     shop_card = models.ForeignKey(ShopCard, related_name='items', on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.product.name} - {self.quantity}"