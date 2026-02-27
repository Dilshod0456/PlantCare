from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ProductCategory, Product, ProductReview,
    Cart, CartItem, Order, OrderItem, Wishlist
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'slug', 'display_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name_uz', 'name_en', 'name_ru')
    prepopulated_fields = {'slug': ('name_uz',)}
    ordering = ['display_order', 'name_uz']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name_uz', 'name_en', 'name_ru', 'slug', 'description')
        }),
        ('Ko\'rinish', {
            'fields': ('icon', 'image', 'display_order', 'is_active')
        }),
        ('Sanalar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'created_at')
    fields = ('user', 'rating', 'title', 'is_approved', 'created_at')
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_preview', 'name', 'category', 'price', 'stock_status',
        'is_featured', 'views_count', 'sales_count', 'is_active'
    )
    list_filter = ('category', 'is_featured', 'is_active', 'is_available', 'care_level', 'condition')
    search_fields = ('name', 'description', 'meta_keywords')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('views_count', 'sales_count', 'created_at', 'updated_at', 'created_by')
    inlines = [ProductReviewInline]
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'slug', 'category', 'plant_type')
        }),
        ('Tavsif', {
            'fields': ('short_description', 'description')
        }),
        ('Rasmlar', {
            'fields': ('main_image', 'image_2', 'image_3', 'image_4')
        }),
        ('Narx va Inventar', {
            'fields': ('price', 'original_price', 'stock_quantity', 'min_order_quantity', 'max_order_quantity')
        }),
        ('O\'simlik ma\'lumotlari', {
            'fields': ('condition', 'height', 'pot_size', 'age', 'care_level')
        }),
        ('Parvarish qilish', {
            'fields': ('light_requirement', 'water_requirement', 'temperature_range'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Holat', {
            'fields': ('is_featured', 'is_active', 'is_available')
        }),
        ('Statistika', {
            'fields': ('views_count', 'sales_count', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.main_image.url
            )
        return '-'
    image_preview.short_description = 'Rasm'
    
    def stock_status(self, obj):
        if obj.stock_quantity > 10:
            color = 'green'
            text = f'✓ {obj.stock_quantity} dona'
        elif obj.stock_quantity > 0:
            color = 'orange'
            text = f'⚠ {obj.stock_quantity} dona'
        else:
            color = 'red'
            text = '✗ Tugadi'
        return format_html('<span style="color: {};">{}</span>', color, text)
    stock_status.short_description = 'Omborda'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'would_recommend', 'created_at')
    list_filter = ('is_approved', 'rating', 'would_recommend', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('helpful_count', 'created_at', 'updated_at')
    actions = ['approve_reviews', 'reject_reviews']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('product', 'user', 'rating', 'title', 'comment', 'would_recommend')
        }),
        ('Rasmlar', {
            'fields': ('image_1', 'image_2'),
            'classes': ('collapse',)
        }),
        ('Moderation', {
            'fields': ('is_approved', 'approved_by')
        }),
        ('Statistika', {
            'fields': ('helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True, approved_by=request.user)
        self.message_user(request, f'{updated} ta sharh tasdiqlandi')
    approve_reviews.short_description = 'Tanlangan sharhlarni tasdiqlash'
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} ta sharh rad etildi')
    reject_reviews.short_description = 'Tanlangan sharhlarni rad etish'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'subtotal', 'added_at')
    can_delete = False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price_display', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'total_price_display')
    inlines = [CartItemInline]
    
    def total_price_display(self, obj):
        return f"{obj.total_price:,.0f} so'm"
    total_price_display.short_description = 'Jami narx'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'full_name', 'phone',
        'status_badge', 'payment_method', 'total_display',
        'is_paid', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'is_paid', 'created_at')
    search_fields = ('order_number', 'user__username', 'full_name', 'phone', 'email')
    readonly_fields = (
        'order_number', 'created_at', 'updated_at',
        'confirmed_at', 'delivered_at', 'subtotal', 'total'
    )
    inlines = [OrderItemInline]
    actions = ['mark_confirmed', 'mark_processing', 'mark_shipped', 'mark_delivered']
    
    fieldsets = (
        ('Buyurtma ma\'lumotlari', {
            'fields': ('order_number', 'user', 'status', 'is_paid')
        }),
        ('Mijoz ma\'lumotlari', {
            'fields': ('full_name', 'phone', 'email')
        }),
        ('Yetkazib berish', {
            'fields': ('address', 'city', 'region', 'postal_code', 'delivery_notes')
        }),
        ('To\'lov', {
            'fields': ('payment_method', 'subtotal', 'delivery_fee', 'discount_amount', 'total')
        }),
        ('Sanalar', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'processing': 'purple',
            'shipped': 'teal',
            'delivered': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Holat'
    
    def total_display(self, obj):
        return f"{obj.total:,.0f} so'm"
    total_display.short_description = 'Jami'
    
    def mark_confirmed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='confirmed', confirmed_at=timezone.now())
        self.message_user(request, 'Buyurtmalar tasdiqlandi')
    mark_confirmed.short_description = 'Tasdiqlandi deb belgilash'
    
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, 'Tayyorlanmoqda deb belgilandi')
    mark_processing.short_description = 'Tayyorlanmoqda deb belgilash'
    
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, 'Jo\'natildi deb belgilandi')
    mark_shipped.short_description = 'Jo\'natildi deb belgilash'
    
    def mark_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, 'Yetkazildi deb belgilandi')
    mark_delivered.short_description = 'Yetkazildi deb belgilash'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'products_count', 'updated_at')
    search_fields = ('user__username',)
    filter_horizontal = ('products',)
    readonly_fields = ('created_at', 'updated_at', 'products_count')
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Mahsulotlar soni'
