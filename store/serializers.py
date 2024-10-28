from decimal import Decimal
from django.utils.text import slugify
from rest_framework import serializers, status
from store.models import Category, Product, Comment, Cart, CartItem


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



