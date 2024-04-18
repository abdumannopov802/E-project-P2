from django.urls import path
# from django.conf.urls import url
from .views import *


urlpatterns = [
    # path('', Home.as_view()),
    # path('category', CategoryAPIView.as_view()),

    path('create-category/', create_category),
    path('get-categories/', get_categories),
    path('update-category/<int:pk>', update_category),
    path('delete-category/<int:pk>', delete_category),

    path('create-customer/', create_customer),
    path('get-customers/', get_customers),
    path('update-customer/<int:pk>', update_customer),
    path('delete-customer/<int:pk>', delete_customer),

    path('create-product/', create_product),
    path('get-products/', get_products),
    path('update-product/<int:pk>', update_product),
    path('delete-product/<int:pk>', delete_product),

    path('create-shopcart/', create_shopcart),
    path('get-shopcarts/', get_shopcarts),
    path('update-shopcart/<int:pk>', update_shopcart),
    path('delete-shopcart/<int:pk>', delete_shopcart),

    path('create-item/', create_item),
    path('get-items/', get_items),
    path('update-item/<int:pk>', update_item),
    path('delete-item/<int:pk>', delete_item),

    path('get-expired-products', get_expired_products),
    path('get-customer-shop-cart/<int:pk>', get_customer_shopcart),
    path('get-all-products-total', get_all_products_total),
    path('most-purchased-products', most_purchased_products),
    path('customer-total-purchase/<int:pk>', customer_total_purchase),

    path('add-to-cart/<int:pk>', add_to_cart),
]