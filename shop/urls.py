from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'shop'

# REST API Router
router = DefaultRouter()
router.register(r'categories', views.ProductCategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'reviews', views.ProductReviewViewSet, basename='review')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

# Template URLs
urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Template views
    path('', views.shop_home, name='home'),
    path('mahsulotlar/', views.product_list, name='product_list'),
    path('mahsulotlar/<slug:slug>/', views.product_detail, name='product_detail'),
    path('savat/', views.cart_view, name='cart'),
    path('buyurtma/', views.checkout, name='checkout'),
    path('buyurtmalarim/', views.order_list, name='order_list'),
    path('buyurtmalarim/<str:order_number>/', views.order_detail, name='order_detail'),
    path('sevimlilar/', views.wishlist_view, name='wishlist'),
]
