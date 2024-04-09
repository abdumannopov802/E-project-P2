from django.urls import path
from .views import *

urlpatterns = [
    # path('', Home.as_view()),

    path('create-category/', create_category),
    path('get-category/', get_categories),
    path('update-category/<int:pk>', update_category),
    path('delete-category/<int:pk>', delete_category),

    path('create-product/', create_product),
    # path('get-products/', views.get_categories),
    # path('update-product/<int:pk>', views.update_category),
    # path('delete-product/<int:pk>', views.delete_category),

]
