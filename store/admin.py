from django.contrib import admin
from .models import Category, Customer, Product, ShopCard, Item

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ShopCard)
admin.site.register(Item)