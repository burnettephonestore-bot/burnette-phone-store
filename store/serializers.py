from rest_framework import serializers
from .models import Product, Update, Request, Cart, UserProfile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ('user', 'phone', 'address', 'city', 'region', 'district')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'media_file', 'media_url', 'media_type', 'created_at')


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = ('id', 'title', 'content', 'media_file', 'media_url', 'type', 'valid_until', 'created_at')


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('id', 'product', 'product_name', 'base_price', 'discount', 'final_price', 'contact_name', 'contact_phone', 'contact_email', 'wants_delivery', 'region', 'district', 'payment_method', 'payment_target', 'status', 'created_at')


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    user = UserSerializer()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'product', 'quantity', 'added_at', 'total_price')