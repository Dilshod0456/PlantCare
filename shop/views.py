from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import (
    ProductCategory, Product, ProductReview,
    Cart, CartItem, Order, OrderItem, Wishlist
)
from .serializers import (
    ProductCategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductReviewSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer, WishlistSerializer
)


# ==================== ViewSets for REST API ====================

class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Mahsulot kategoriyalari API"""
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Mahsulotlar API"""
    queryset = Product.objects.filter(is_active=True, is_available=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['price', 'created_at', 'views_count', 'sales_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by plant type
        plant_type = self.request.query_params.get('plant_type', None)
        if plant_type:
            queryset = queryset.filter(plant_type__code=plant_type)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by care level
        care_level = self.request.query_params.get('care_level', None)
        if care_level:
            queryset = queryset.filter(care_level=care_level)
        
        # Filter featured
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # In stock only
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Mahsulot sharhlari"""
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ProductReviewViewSet(viewsets.ModelViewSet):
    """Mahsulot sharhlari API"""
    queryset = ProductReview.objects.filter(is_approved=True)
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Sharhni foydali deb belgilash"""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        return Response({'helpful_count': review.helpful_count})


class CartViewSet(viewsets.ModelViewSet):
    """Savat API"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Savatga mahsulot qo'shish"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True, is_available=True)
            
            # Check stock
            if product.stock_quantity < quantity:
                return Response(
                    {'error': 'Omborda yetarli mahsulot yo\'q'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        
        except Product.DoesNotExist:
            return Response(
                {'error': 'Mahsulot topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Savatdagi mahsulot miqdorini o'zgartirish"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            cart_item = cart.items.get(id=item_id)
            
            if quantity <= 0:
                cart_item.delete()
            else:
                if cart_item.product.stock_quantity < quantity:
                    return Response(
                        {'error': 'Omborda yetarli mahsulot yo\'q'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = quantity
                cart_item.save()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Savat elementi topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Savatdan mahsulotni o'chirish"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Savat elementi topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Savatni tozalash"""
        cart = self.get_object()
        cart.clear()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """Buyurtmalar API"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Buyurtma yaratish"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Savatingiz bo\'sh'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cart.items.count() == 0:
            return Response(
                {'error': 'Savatingiz bo\'sh'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate totals
        subtotal = cart.total_price
        delivery_fee = 20000  # 20,000 so'm
        discount_amount = 0
        total = subtotal + delivery_fee - discount_amount
        
        # Create order
        order = serializer.save(
            user=request.user,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount_amount=discount_amount,
            total=total
        )
        
        # Create order items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
            
            # Update product stock
            product = cart_item.product
            product.stock_quantity -= cart_item.quantity
            product.sales_count += cart_item.quantity
            product.save()
        
        # Clear cart
        cart.clear()
        
        # Return order details
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Buyurtmani bekor qilish"""
        order = self.get_object()
        
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Bu buyurtmani bekor qilib bo\'lmaydi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        # Restore stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.sales_count -= item.quantity
            product.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class WishlistViewSet(viewsets.ModelViewSet):
    """Sevimlilar API"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist
    
    @action(detail=False, methods=['post'])
    def add_product(self, request):
        """Mahsulotni sevimlilarga qo'shish"""
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            wishlist.products.add(product)
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Mahsulot topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_product(self, request):
        """Mahsulotni sevimlilardan o'chirish"""
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            wishlist.products.remove(product)
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Mahsulot topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )


# ==================== Template Views ====================

def shop_home(request):
    """Do'kon bosh sahifasi"""
    categories = ProductCategory.objects.filter(is_active=True)
    featured_products = Product.objects.filter(
        is_active=True, is_available=True, is_featured=True
    )[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'shop/home.html', context)


def product_list(request):
    """Mahsulotlar ro'yxati"""
    products = Product.objects.filter(is_active=True, is_available=True)
    
    # Filters
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ProductCategory.objects.filter(is_active=True)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, slug):
    """Mahsulot tafsilotlari"""
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )
    product.increment_views()
    
    # Reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user,
            products=product
        ).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'shop/product_detail.html', context)


@login_required
def cart_view(request):
    """Savat sahifasi"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    context = {
        'cart': cart,
        'delivery_fee': 20000,
    }
    return render(request, 'shop/cart.html', context)


@login_required
def checkout(request):
    """Buyurtmani rasmiylashtirish"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if cart.items.count() == 0:
        return redirect('shop:cart')
    
    if request.method == 'POST':
        # Handle order creation via form
        pass
    
    delivery_fee = 20000
    total = cart.total_price + delivery_fee
    
    context = {
        'cart': cart,
        'delivery_fee': delivery_fee,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def order_list(request):
    """Foydalanuvchi buyurtmalari"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Buyurtma tafsilotlari"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)


@login_required
def wishlist_view(request):
    """Sevimlilar sahifasi"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    context = {
        'wishlist': wishlist,
    }
    return render(request, 'shop/wishlist.html', context)
