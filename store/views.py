from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from .postgres import postgres
import jwt

from datetime import date
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Cast
from rest_framework.views import APIView

from django.contrib.auth.decorators import login_required, permission_required


from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

# class Home(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         barer_token = request.headers['Authorization']
#         barer_token = barer_token.split(' ')[1]
#         decode = jwt.decode(barer_token, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEzMTc3MTA1LCJpYXQiOjE3MTIzMTMxMDUsImp0aSI6ImZmZDVkMTBjMGUwYjQ3OWNiNTI0M2YxYjkxOWE2MDRhIiwidXNlcl9pZCI6MX0.I_pqpyQktdfaVPDRwsS7V78-r-YN992YGuwgIHIk8KE"')
#         id = decode['user_id']
#         obj = User.objects.get(id=id)
#         mod = UserSerializer(obj)
#         return Response(mod.data)

# class CategoryAPIView(APIView):
#     @swagger_auto_schema(request_body=CategorySerializer)
#     def post(self, request):
#         new_category = CategorySerializer(data=request.data)
#         if new_category.is_valid():
#             category = Category.objects.create(name=request.data['name'])
#             category.save()
#             return Response(new_category.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(new_category.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     @swagger_auto_schema()
#     def get(self, request):
#         category_list = get_list_or_404(Category)
#         serializered_categories = CategorySerializer(category_list, many=True)
#         return Response(serializered_categories.data, status=status.HTTP_200_OK)

#     @swagger_auto_schema(request_body=CategoryUpdateSerializer)
#     def patch(self, request, pk):
#         try:
#             category_obj = get_object_or_404(Category, pk=pk)
#             updating_category = CategoryUpdateSerializer(category_obj, data=request.data, partial=True)
#             if updating_category.is_valid():
#                 updating_category.save()
#                 return Response({'Message': 'Category updated'}, status=status.HTTP_200_OK)
#             else:
#                 return Response(updating_category.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as error:
#             return Response({"Error": f'{error}'}, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(request_body=ProductSerializer)
#     def delete(self, request, pk):
#         category = get_object_or_404(Category, pk=pk)
#         category.delete()
#         return Response({"Message": "Category deleted"}, status=status.HTTP_200_OK)

# 3 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
def get_customer_shopcart(request, pk):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, pk=pk)
        purchase_history = Item.objects.filter(shop_card__customer=customer)
        serializered_list = ProductSerializer(purchase_history, many=True)
        return Response(serializered_list.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# 4 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
def customer_total_purchase(request, pk):
    if request.method == 'GET':
        total_purchase_sum = (
            PurchaseHistory.objects.filter(customer_id=pk)
            .aggregate(total_sum=Sum(F('product__price') * F('quantity')))
        )
        total_sum = total_purchase_sum['total_sum'] if total_purchase_sum['total_sum'] else 0
        return Response(total_sum, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
# 5 <<<<< 

@swagger_auto_schema(method='GET')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_all_products_total(request):
    if request.method == 'GET':
        product_list = get_list_or_404(Product)
        total_sum = sum(product.price for product in product_list)
        return Response(total_sum, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# 6 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
def get_expired_products(request):
    if request.method == 'GET':
        today = date.today()
        product_list = Product.objects.filter(expired_date__lt=today)
        serializered_list = ProductSerializer(product_list, many=True)
        return Response(serializered_list.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# 7 <<<<<
@swagger_auto_schema(method='GET')
@api_view(['GET'])
def most_purchased_products(request):
    if request.method == 'GET':
        product_quantities = (
            PurchaseHistory.objects.values('product_id')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
        )
        top_products = Product.objects.filter(id__in=[item['product_id'] for item in product_quantities[:5]])
        return Response(top_products, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

# ADD TO CART
@swagger_auto_schema(method='GET')
@api_view(['POST'])
def add_to_cart(request, pk):
    try:
        # Retrieve the product
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create the user's cart
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    cart, _ = ShopCard.objects.get_or_create(customer=user.customer, complete=False)
    
    # Check if the item is already in the cart
    existing_item = cart.item_set.filter(product=product).first()
    if existing_item:
        existing_item.quantity += 1
        existing_item.save()
    else:
        Item.objects.create(product=product, cart=cart, quantity=1)
    
    # Serialize the updated cart and return it
    serializer = ShopCardSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)

        

# CRUD Category <<<<<

@swagger_auto_schema(method='POST', request_body=CategorySerializer)
@api_view(['POST'])
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
    
@swagger_auto_schema(method='DELETE', request_body=ProductSerializer)
@api_view(['DELETE'])
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
def get_customers(request):
    if request.method == 'GET':
        customer_list = get_list_or_404(Customer)
        serializered_customers = CustomerSerializer(customer_list, many=True)
        return Response(serializered_customers.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=ProductUpdateSerializer)
@api_view(['PATCH'])
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
    
@swagger_auto_schema(method='DELETE', request_body=ProductSerializer)
@api_view(['DELETE'])
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
def get_shopcarts(request):
    if request.method == 'GET':
        shopcart_list = get_list_or_404(ShopCard)
        serializered_shopcarts = ProductSerializer(shopcart_list, many=True)
        return Response(serializered_shopcarts.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=ShopCardSerializer)
@api_view(['PATCH'])
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
def get_items(request):
    if request.method == 'GET':
        item_list = get_list_or_404(Item)
        serializered_items = ItemSerializer(item_list, many=True)
        return Response(serializered_items.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=ItemSerializer)
@api_view(['PATCH'])
def update_item(request, pk):
    if request.method == 'PATCH':
        try:
            item = Item.objects.get(pk=pk)
            updating_item = ItemSerializer(item, data=request.data, partial=True)
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
def delete_item(request, pk):
    if request.method == 'DELETE':
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return Response({"Message": "Item deleted"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse

@permission_required('polls.add_choice', login_url='/loginpage/')
def my_view(request):
    # Check if user has permission
    if request.user.has_perm('polls.add_choice'):
        # User has permission, so perform desired action
        return HttpResponse("You have permission to add choices.")
    else:
        # User does not have permission
        return HttpResponse("You do not have permission to add choices.")