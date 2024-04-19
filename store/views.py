from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

from datetime import date
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from datetime import date
today = date.today()

# 3 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def get_costumer_history(request, pk):
    if request.method == 'GET':
        costumer_history = get_list_or_404(CostumerHistory, customer=pk)
        serializered_list = CostumerHistorySerializer(costumer_history, many=True)
        return Response(serializered_list.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# 4 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def costumer_total_purchase(request, pk):
    if request.method == 'GET':
        costumer_history = get_list_or_404(CostumerHistory, customer=pk)
        total_sum = 0
        for item in costumer_history:
            total_sum += (item.product.price * item.quantity)
        if total_sum >= 1000000:
            return Response({'Congratulate': f'This costumer total purchase {total_sum} uzs'}, status=status.HTTP_200_OK)
        return Response({'Message': f'Purchase not over 1.000.000 yet, total: {total_sum} uzs'}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
# 5 <<<<< 
@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def get_all_products_total(request):
    if request.method == 'GET':
        valid_products = Product.objects.filter(expire_date__gt=today)
        if valid_products:
            total_sum = sum(product.price for product in valid_products)
            return Response({'Message': f'Total product amount in the market: {total_sum} uzs'}, status=status.HTTP_200_OK)
        else:
            return Response({'Message': 'No product available.!'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# 6 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def get_expired_products(request):
    if request.method == 'GET':
        valid_products = Product.objects.filter(expired_date__lt=today)
        if valid_products:
            serializered_list = ProductSerializer(valid_products, many=True)
            return Response(serializered_list.data, status=status.HTTP_200_OK)
        else:
            return Response({'Message': 'No product available.!'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# 7 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def most_purchased_products(request):
    if request.method == 'GET':
        most_purchased = CostumerHistory.objects.values('product').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:1]
        product_ids = [entry['product'] for entry in most_purchased]
        most_purchased_products = get_list_or_404(Product, id__in=product_ids)
        serializer = ProductSerializer(most_purchased_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# ADD TO CART
@swagger_auto_schema(method='POST')
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    cart, _ = ShopCard.objects.get_or_create(customer=user.customer)
    
    existing_item = cart.item_set.filter(product=product).first()
    if existing_item:
        existing_item.quantity += 1
        existing_item.save()
    else:
        Item.objects.create(product=product, cart=cart, quantity=1)
    
    serializer = ShopCardSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ACTIVATE ORDER
@swagger_auto_schema(method='POST')
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def activate_order(request):
    if request.method == 'POST':
        user_cart_items = ShopCard.objects.filter(customer=request.user.customer)
        if user_cart_items.exists():
            for card in user_cart_items:
                for item in card.item_set.all():  # Assuming each ShopCard has multiple related Item objects
                    CostumerHistory.objects.create(customer=request.user.customer, product=item.product, quantity=item.quantity)
            user_cart_items.delete()
            return Response({"Message": "Customer orders were ACTIVATED"}, status=status.HTTP_200_OK)
        else:
            return Response({"Message": "Customer Shop Cart is empty"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# CRUD Category <<<<<

@swagger_auto_schema(method='POST', request_body=CategorySerializer)
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def create_category(request):
    if request.method == 'POST':
        new_category = CategorySerializer(data=request.data)
        if new_category.is_valid():
            category = Category.objects.create(name=request.data['name'])
            category.save()
            return Response(new_category.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_category.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_categories(request):
    if request.method == 'GET':
        category_list = get_list_or_404(Category)
        serializered_categories = CategorySerializer(category_list, many=True)
        return Response(serializered_categories.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=CategoryUpdateSerializer)
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def update_category(request, pk):
    if request.method == 'PATCH':
        try:
            category_obj = get_object_or_404(Category, pk=pk)
            updating_category = CategoryUpdateSerializer(category_obj, data=request.data, partial=True)
            if updating_category.is_valid():
                updating_category.save()
                return Response({'Message': 'Category updated'}, status=status.HTTP_200_OK)
            else:
                return Response(updating_category.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"Error": f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=CategorySerializer)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def delete_category(request, pk):
    if request.method == 'DELETE':
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response({"Message": "Category deleted"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)


# CRUD Customer

@swagger_auto_schema(method='POST', request_body=CustomerSerializer)
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_customer(request):
    if request.method == 'POST':
        new_customer = CustomerSerializer(data=request.data)
        if new_customer.is_valid():
            new_customer.save()
            return Response(new_customer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_customer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_customers(request):
    if request.method == 'GET':
        customer_list = get_list_or_404(Customer)
        serializered_customers = CustomerSerializer(customer_list, many=True)
        return Response(serializered_customers.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=CustomerUpdateSerializer)
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_customer(request, pk):
    if request.method == 'PATCH':
        try:
            customer_obj = Customer.objects.get(pk=pk)
            updating_customer = CustomerUpdateSerializer(customer_obj, data=request.data, partial=True)
            if updating_customer.is_valid():
                updating_customer.save()
                return Response({'Message': 'Customer updated'}, status=status.HTTP_200_OK)
            else:
                return Response(updating_customer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"Error": f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=CustomerSerializer)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def delete_customer(request, pk):
    if request.method == 'DELETE':
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response({"Message": "Customer deleted"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)


# CRUD Product

@swagger_auto_schema(method='POST', request_body=ProductSerializer)
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def create_product(request):
    if request.method == 'POST':
        new_product = ProductSerializer(data=request.data)
        if new_product.is_valid():
            new_product.save()
            return Response(new_product.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_product.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_products(request):
    if request.method == 'GET':
        product_list = get_list_or_404(Product)
        serializered_products = ProductSerializer(product_list, many=True)
        return Response(serializered_products.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=ProductUpdateSerializer)
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def update_product(request, pk):
    if request.method == 'PATCH':
        try:
            product_obj = Product.objects.get(pk=pk)
            updating_product = ProductUpdateSerializer(product_obj, data=request.data, partial=True)
            if updating_product.is_valid():
                updating_product.save()
                return Response({'Message': 'Product updated'}, status=status.HTTP_200_OK)
            else:
                return Response(updating_product.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"Error": f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=ProductSerializer)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def delete_product(request, pk):
    if request.method == 'DELETE':
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response({"Message": "Product deleted"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)


# CRUD ShopCart

@swagger_auto_schema(method='POST', request_body=ShopCardSerializer)
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_shopcart(request):
    if request.method == 'POST':
        new_shopcart = ShopCardSerializer(data=request.data)
        if new_shopcart.is_valid():
            new_shopcart.save()
            return Response(new_shopcart.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_shopcart.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_shopcarts(request):
    if request.method == 'GET':
        shopcart_list = get_list_or_404(ShopCard)
        serializered_shopcarts = ProductSerializer(shopcart_list, many=True)
        return Response(serializered_shopcarts.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=ShopCardSerializer)
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_shopcart(request, pk):
    if request.method == 'PATCH':
        try:
            shopcart = ShopCard.objects.get(pk=pk)
            updating_shopcart = ShopCardSerializer(shopcart, data=request.data, partial=True)
            if updating_shopcart.is_valid():
                updating_shopcart.save()
                return Response({'Message': 'ShopCart updated'}, status=status.HTTP_200_OK)
            else:
                return Response(updating_shopcart.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"Error": f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=ShopCardSerializer)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def delete_shopcart(request, pk):
    if request.method == 'DELETE':
        shopcart = get_object_or_404(ShopCard, pk=pk)
        shopcart.delete()
        return Response({"Message": "Shopcart deleted"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    

# CRUD Items

@swagger_auto_schema(method='POST', request_body=ItemSerializer)
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_item(request):
    if request.method == 'POST':
        new_item = ItemSerializer(data=request.data)
        if new_item.is_valid():
            new_item.save()
            return Response(new_item.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_item.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_items(request):
    if request.method == 'GET':
        item_list = get_list_or_404(Item)
        serializered_items = ItemSerializer(item_list, many=True)
        return Response(serializered_items.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=ItemUpdateSerializer)
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_item(request, pk):
    if request.method == 'PATCH':
        try:
            item = Item.objects.get(pk=pk)
            updating_item = ItemUpdateSerializer(item, data=request.data, partial=True)
            if updating_item.is_valid():
                updating_item.save()
                return Response({'Message': 'Item updated'}, status=status.HTTP_200_OK)
            else:
                return Response(updating_item.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"Error": f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=ItemSerializer)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def delete_item(request, pk):
    if request.method == 'DELETE':
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return Response({"Message": "Item deleted"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    

# CRUD Admin

@swagger_auto_schema(method='POST', request_body=AdminSerializer)
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def create_admin(request):
    if request.method == 'POST':
        new_admin = AdminSerializer(data=request.data)
        if new_admin.is_valid():
            new_admin.save()
            return Response(new_admin.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_admin.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def get_admin(request):
    if request.method == 'GET':
        admin_list = get_list_or_404(Admin)
        serializer = AdminSerializer(admin_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=AdminUpdateSerializer)
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def update_admin(request, pk):
    if request.method == 'PATCH':
        try:
            admin = Admin.objects.get(pk=pk)
            patch_admin = AdminUpdateSerializer(admin, data=request.data, partial=True)
            if patch_admin.is_valid():
                patch_admin.save()
                return Response({'Message': 'Admin updated'}, status=status.HTTP_200_OK)
            else:
                return Response(patch_admin.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"Error": f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=AdminSerializer)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def delete_admin(request, pk):
    if request.method == 'DELETE':
        item = get_object_or_404(Admin, pk=pk)
        item.delete()
        return Response({"Message": "Admin deleted"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    

# Authentication <<<<<
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm
# signup page
def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'sign-up.html', {'form': form})

# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'log-in.html', {'form': form})

# logout page
def user_logout(request):
    logout(request)
    return redirect('/')