from decimal import Decimal
from django.utils.text import slugify
from rest_framework import serializers, status
from django.db import transaction
from core.models import CustomUser
from store.models import Category, Product, Comment, Cart, CartItem, Customer, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields = ['title','description','number_of_products']
    number_of_products = serializers.SerializerMethodField()

    def get_number_of_products(self,category):
        return (category.products.count())

    def validate(self, data):

        if len(data['title']) < 3:
            raise serializers.ValidationError('the length of title MUST be more than 3 charachters')
        else:
            return data



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields= ['id','name','unit_price','category','discount_price','inventory','slug']


    discount_price = serializers.SerializerMethodField()

    def get_discount_price(self,product):
        return product.unit_price * Decimal(0.09)

    def validate(self, data):
        if len(data['name'])< 6:
            raise serializers.ValidationError('length of name MUST be more than 6')
        return data


    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product

    def update(self, instance, validated_data):
        instance.slug=slugify(instance.name)
        instance.save()
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['name','body']

    def create(self, validated_data):
        product_pk = self.context['product_pk']
        return Comment.objects.create(product_id=product_pk,**validated_data)


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields= ['id','name','unit_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id','product','quantity']

    def create(self, validated_data):
        cart_id = self.context.get('cart_pk')
        product = validated_data.get('product')
        if CartItem.objects.filter(cart_id=cart_id,product_id=product.id).exists():
            cart_item = CartItem.objects.get(cart_id=cart_id,product_id=product.id)
            cart_item.quantity += validated_data.get('quantity')

            cart_item.save()
            return cart_item


        return CartItem.objects.create(cart_id=cart_id,
                                      **validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    item_total = serializers.SerializerMethodField()

    def get_item_total(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id','product','quantity','item_total']


class CartSerializers(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cart):
        return sum(item.quantity*item.product.unit_price for item in cart.items.all())

    class Meta:
        model = Cart
        fields = ['id','items','total_price']
        read_only_fields = ['id', ]

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id','user','birth_date',]
        read_only_fields = ['user',]
    user = CustomUserSerializer()

class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','unit_price']
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','unit_price']

    product = OrderItemProductSerializer()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerSerializer()

    class Meta:
        model = Order
        fields = ['id','customer','status','datetime_created','items']


class OrderCustomerSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'status', 'datetime_created', 'items']

class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            return serializers.ValidationError('no cart')
        if CartItem.objects.filter(cart_id=cart_id).all().count()==0:
            return serializers.ValidationError('there is not items in your cart')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id).all()
            order_item_list=list()
            for item in cart_items:
                order_item = OrderItem()
                order_item.order = order
                order_item.product_id = item.product_id
                order_item.unit_price = item.product.unit_price
                order_item.quantity = item.quantity
                order_item_list.append(order_item)
            OrderItem.objects.bulk_create(order_item_list)
            Cart.objects.get(id=cart_id).delete()
            return order




