from django.contrib import admin
from .models import Category, Customer, Product, ShopCard, Item, Admin, CostumerHistory

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name', 'description')  # Adding filter for Category

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('name', 'email', 'phone_number')  # Adding filter for Customer

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'expire_date')
    list_filter = ('category', 'expire_date', 'price')  # Adding filter for Product
    search_fields = ('name',)

@admin.register(ShopCard)
class ShopCardAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'get_cart_total', 'get_cart_items')
    search_fields = ('customer__name',)
    list_filter = ('customer', 'date')  # Adding filter for ShopCard

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'date_added', 'get_total')
    search_fields = ('cart__id',)
    list_filter = ('product', 'cart', 'quantity', 'date_added')  # Adding filter for Item

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('name', 'email', 'phone_number')  # Adding filter for Admin

@admin.register(CostumerHistory)
class CostumerHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'purchase_date')
    list_filter = ('customer', 'product', 'quantity', 'purchase_date')  # Adding filter for CostumerHistory
    search_fields = ('customer__name', 'product__name')
