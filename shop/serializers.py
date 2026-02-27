from rest_framework import serializers
from .models import (
    ProductCategory, Product, ProductReview,
    Cart, CartItem, Order, OrderItem, Wishlist
)
from diagnosis.models import PlantType


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class PlantTypeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantType
        fields = ['id', 'code', 'name_uz', 'name_en', 'name_ru']


class ProductListSerializer(serializers.ModelSerializer):
    """Mahsulotlar ro'yxati uchun"""
    category_name = serializers.CharField(source='category.name_uz', read_only=True)
    plant_type_name = serializers.CharField(source='plant_type.name_uz', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'plant_type', 'plant_type_name', 'short_description',
            'main_image', 'price', 'original_price', 'stock_quantity',
            'is_in_stock', 'has_discount', 'discount_percentage',
            'average_rating', 'is_featured', 'condition', 'care_level'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Mahsulot tafsilotlari uchun"""
    category = ProductCategorySerializer(read_only=True)
    plant_type = PlantTypeSimpleSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'user_name', 'rating',
            'title', 'comment', 'would_recommend',
            'image_1', 'image_2', 'helpful_count', 'created_at'
        ]
        read_only_fields = ['user', 'helpful_count', 'created_at']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['subtotal', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 'updated_at']
        read_only_fields = ['user', 'total_items', 'total_price']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']
        read_only_fields = ['product_name', 'product_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'order_number', 'user', 'subtotal', 'total',
            'created_at', 'updated_at', 'confirmed_at', 'delivered_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Buyurtma yaratish uchun"""
    
    class Meta:
        model = Order
        fields = [
            'full_name', 'phone', 'email', 'address',
            'city', 'region', 'postal_code', 'delivery_notes',
            'payment_method'
        ]


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products', 'product_ids', 'updated_at']
        read_only_fields = ['user']