from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .connection import postgres
import jwt

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication

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
    

# CRUD Category

@swagger_auto_schema(method='POST', request_body=CategorySerializer)
@api_view(['POST'])
def create_category(request):
    if request.method == 'POST':
        new_category = CategorySerializer(data=request.data)
        if new_category.is_valid():
            category = Category.objects.create(name=request.data['name'])
            category.save()
            return Response({'Success' : f'New <{category.name}> category has created'}, status=status.HTTP_201_CREATED)
        else:
            return Response(new_category.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='GET')
@api_view(['GET'])
def get_categories(request):
    if request.method == 'GET':
        category_list = get_list_or_404(Category)
        serializered_categories = CategorySerializer(category_list, many=True)
        return Response(serializered_categories.data, status=status.HTTP_200_OK)
    else:
        Response({"Error": "Unexpected error occured."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=CategoryUpdateSerializer)
@api_view(['PATCH'])
def update_category(request, pk):
    if request.method == 'PATCH':
        try:
            category_obj = get_object_or_404(Category, pk=pk)
            updating_category_obj = CategoryUpdateSerializer(category_obj, data=request.data, partial=True)
            if updating_category_obj.is_valid():
                updating_category_obj.save()
                return Response({'Success': 'Category has updated'}, status=status.HTTP_200_OK)
            else:
                return Response(updating_category_obj.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error": f"Unexpected error {e} occured."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=ProductSerializer)
@api_view(['DELETE'])
def delete_category(request, pk):
    if request.method == 'DELETE':
        category_ogj = get_object_or_404(Category, pk=pk)
        category_ogj.delete()
        return Response({"Message": f"Category have been deleted, id: {pk}"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)


# CRUD Product

@swagger_auto_schema(method='POST', request_body=ProductSerializer)
@api_view(['POST'])
def create_product(request):
    if request.method == 'POST':
        new_product = ProductSerializer(data=request.data)
        if new_product.is_valid():
            name = request.data['name']
            price = request.data['price']
            category = request.data['category']
            new_product = Product.objects.create(name=name, price=price, category=category)
            new_product.save()
            return Response(new_product.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_product.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_products(request):
    if request.method == 'GET':
        product_list = get_list_or_404(Product)
        serializered_products = ProductSerializer(product_list, many=True)
        return Response(serializered_products.data, status=status.HTTP_200_OK)
    else:
        Response(serializered_products.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='PATCH', request_body=ProductUpdateSerializer)
@api_view(['PATCH'])
def update_product(request, pk):
    if request.method == 'PATCH':
        try:
            category_obj = Product.objects.get(pk=pk)
            updating_product_obj = ProductUpdateSerializer(category_obj, data=request.data, partial=True)
            if updating_product_obj.is_valid():
                updating_product_obj.save()
                return Response({'Message': 'Category updated'}, status=status.HTTP_200_OK)
            else:
                return Response(updating_product_obj.error, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error": f"Unexpected error {e} occured."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='DELETE', request_body=ProductSerializer)
@api_view(['DELETE'])
def delete_product(request, pk):
    if request.method == 'DELETE':
        deleting_product_ogj = get_object_or_404(Product, pk=pk)
        deleting_product_ogj.delete()
        return Response({"Message": f"Product have been deleted, id: {pk}"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Invalid request type"}, status=status.HTTP_400_BAD_REQUEST)
