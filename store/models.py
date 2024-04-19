from django.db import models
from django.contrib.auth.models import User
from datetime import date

from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
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
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expire_date = models.DateField()

    def __str__(self):
        return self.name

class ShopCard(models.Model):
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def get_cart_total(self):
        items = self.item_set.all()  # Access related Item instances using the correct field name
        total = sum(item.get_total for item in items)
        return total

    def get_cart_items(self):
        items = self.item_set.all()  # Access related Item instances using the correct field name
        total = sum(item.quantity for item in items)
        return total

class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey(ShopCard, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.cart)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

class CostumerHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} - {self.purchase_date}"
