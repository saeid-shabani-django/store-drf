from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status, mixins
from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpRequest
from rest_framework.views import Response, APIView
from store.models import Product, Category, Comment, Cart, CartItem
from store.serializers import ProductSerializer, CategorySerializer, CommentSerializer, CartSerializers, \
    CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from rest_framework.filters import OrderingFilter,SearchFilter
from .mypaginations import MyLimitOffsetPagination
from django.contrib.auth.models import User


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'inventory': ['exact',],
            'name':['icontains',],

        }


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter,SearchFilter]
    ordering_fields = ['name','unit_price']
    search_fields = ['name',]
    filterset_class = ProductFilter
    pagination_class = MyLimitOffsetPagination

    queryset = Product.objects.select_related('category').all()

    def get_serializer_context(self):
        return {'request':self.request}

    def destroy(self,request,pk):
        product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
        if product.order_items.count() > 0:
            return Response('it is related to comment , delete it first',
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('products').all()

    def destroy(self,request,pk):
        category = get_object_or_404(Category, pk=pk)
        if len(category.products.all())>0:
            return Response({"error":"this is related to some products , delete them first and try again"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        return Comment.objects.filter(product_id=product_pk)

    def get_serializer_context(self):
        product_pk = self.kwargs['product_pk']
        return {'product_pk':product_pk}


class CartModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                   GenericViewSet):
    serializer_class = CartSerializers
    queryset = Cart.objects.prefetch_related('items__product').all()


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    def get_queryset(self):
        cart_id = self.kwargs['cart_pk']
        if cart_id is not None:
            return CartItem.objects.select_related('product').filter(cart_id=cart_id).all()
        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        cart_id = self.kwargs['cart_pk']
        return {'cart_pk': cart_id}




