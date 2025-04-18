from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User
from .models import (Category,
                     Product,
                     ProductVariant,
                     Cart,
                     CartItem,
                     Order,
                     OrderItem,
                     Payment,
                     ShippingAddress
                     )


class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password',
                  'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, value):
        if value['password'] != value['confirm_password']:
            raise serializers.ValidationError(
                "Password and Confirm Password do not match"
            )
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        if User.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError(
                "Username already exists"
            )
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
        # depth = 1


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'slug', 'parent']
        extra_kwargs = {
            'slug': {'read_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }


class ProductVarientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }
        read_only_fields = ['cart']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }
        read_only_fields = ['order']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'
