from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from diagnosis.models import PlantType


class ProductCategory(models.Model):
    """Mahsulot kategoriyalari"""
    
    name_uz = models.CharField(max_length=100, verbose_name='Nomi (O\'zbek)')
    name_en = models.CharField(max_length=100, blank=True, verbose_name='Nomi (English)')
    name_ru = models.CharField(max_length=100, blank=True, verbose_name='Nomi (Русский)')
    
    slug = models.SlugField(unique=True, verbose_name='URL slug')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icon (FontAwesome)', help_text='Masalan: fa-seedling')
    image = models.ImageField(upload_to='shop/categories/', blank=True, null=True, verbose_name='Rasm')
    
    display_order = models.IntegerField(default=0, verbose_name='Tartib')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name_uz']
        verbose_name = 'Mahsulot kategoriyasi'
        verbose_name_plural = 'Mahsulot kategoriyalari'
    
    def __str__(self):
        return self.name_uz


class Product(models.Model):
    """Suv o'tlari va boshqa o'simliklar mahsulotlari"""
    
    CONDITION_CHOICES = [
        ('new', 'Yangi ko\'chat'),
        ('growing', 'O\'sayotgan'),
        ('mature', 'Pishgan'),
    ]
    
    # Asosiy ma'lumotlar
    name = models.CharField(max_length=200, verbose_name='Mahsulot nomi')
    slug = models.SlugField(unique=True, verbose_name='URL slug')
    
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products', verbose_name='Kategoriya')
    plant_type = models.ForeignKey(PlantType, on_delete=models.SET_NULL, null=True, blank=True, related_name='shop_products', verbose_name='O\'simlik turi')
    
    # Tavsif
    short_description = models.CharField(max_length=255, blank=True, verbose_name='Qisqa tavsif')
    description = models.TextField(verbose_name='To\'liq tavsif')
    
    # Rasmlar
    main_image = models.ImageField(upload_to='shop/products/', verbose_name='Asosiy rasm')
    image_2 = models.ImageField(upload_to='shop/products/', blank=True, null=True, verbose_name='Qo\'shimcha rasm 2')
    image_3 = models.ImageField(upload_to='shop/products/', blank=True, null=True, verbose_name='Qo\'shimcha rasm 3')
    image_4 = models.ImageField(upload_to='shop/products/', blank=True, null=True, verbose_name='Qo\'shimcha rasm 4')
    
    # Narx va inventar
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Narx (so\'m)')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Asl narx (chegirma uchun)')
    
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Ombordagi miqdor')
    min_order_quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Minimal buyurtma')
    max_order_quantity = models.IntegerField(null=True, blank=True, verbose_name='Maksimal buyurtma')
    
    # O'simlik ma'lumotlari
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='growing', verbose_name='Holati')
    height = models.CharField(max_length=50, blank=True, verbose_name='Balandlik', help_text='Masalan: 20-30 sm')
    pot_size = models.CharField(max_length=50, blank=True, verbose_name='Idish o\'lchami', help_text='Masalan: 15 sm diametr')
    age = models.CharField(max_length=50, blank=True, verbose_name='Yoshi', help_text='Masalan: 6 oy')
    
    # Parvarish qilish bo'yicha ma'lumotlar
    care_level = models.CharField(max_length=20, choices=[
        ('easy', 'Oson'),
        ('moderate', 'O\'rtacha'),
        ('difficult', 'Qiyin')
    ], default='moderate', verbose_name='Parvarish qilish darajasi')
    
    light_requirement = models.CharField(max_length=100, blank=True, verbose_name='Yorug\'lik talabi')
    water_requirement = models.CharField(max_length=100, blank=True, verbose_name='Suv talabi')
    temperature_range = models.CharField(max_length=100, blank=True, verbose_name='Harorat oralig\'i')
    
    # SEO va Meta
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta sarlavha')
    meta_description = models.CharField(max_length=300, blank=True, verbose_name='Meta tavsif')
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name='Meta kalit so\'zlar')
    
    # Status
    is_featured = models.BooleanField(default=False, verbose_name='Tanlangan mahsulot')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    is_available = models.BooleanField(default=True, verbose_name='Mavjud')
    
    # Statistika
    views_count = models.IntegerField(default=0, verbose_name='Ko\'rishlar soni')
    sales_count = models.IntegerField(default=0, verbose_name='Sotuvlar soni')
    
    # Sanalar
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_products', verbose_name='Yaratuvchi')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_available']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        """Omborda borligini tekshirish"""
        return self.stock_quantity > 0
    
    @property
    def has_discount(self):
        """Chegirmasi borligini tekshirish"""
        return self.original_price and self.original_price > self.price
    
    @property
    def discount_percentage(self):
        """Chegirma foizini hisoblash"""
        if self.has_discount:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    @property
    def average_rating(self):
        """O'rtacha reyting"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    def increment_views(self):
        """Ko'rishlar sonini oshirish"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ProductReview(models.Model):
    """Mahsulot sharhlari va reytinglari"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Mahsulot')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews', verbose_name='Foydalanuvchi')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Reyting')
    title = models.CharField(max_length=200, blank=True, verbose_name='Sarlavha')
    comment = models.TextField(verbose_name='Sharh')
    
    # Qo'shimcha savollar
    would_recommend = models.BooleanField(default=True, verbose_name='Tavsiya qilasizmi?')
    
    # Rasm yuklash imkoniyati
    image_1 = models.ImageField(upload_to='shop/reviews/', blank=True, null=True, verbose_name='Rasm 1')
    image_2 = models.ImageField(upload_to='shop/reviews/', blank=True, null=True, verbose_name='Rasm 2')
    
    # Moderation
    is_approved = models.BooleanField(default=False, verbose_name='Tasdiqlangan')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reviews', verbose_name='Tasdiqlagan')
    
    # Foydalilik
    helpful_count = models.IntegerField(default=0, verbose_name='Foydali deb topildi')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mahsulot sharhi'
        verbose_name_plural = 'Mahsulot sharhlari'
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"


class Cart(models.Model):
    """Foydalanuvchi savati"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shopping_cart', verbose_name='Foydalanuvchi')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Savatcha'
        verbose_name_plural = 'Savatchalar'
    
    def __str__(self):
        return f"{self.user.username} savati"
    
    @property
    def total_items(self):
        """Jami mahsulotlar soni"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def total_price(self):
        """Jami narx"""
        return sum(item.subtotal for item in self.items.all())
    
    def clear(self):
        """Savatni tozalash"""
        self.items.all().delete()


class CartItem(models.Model):
    """Savatdagi mahsulot"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Savatcha')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Mahsulot')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Miqdor')
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Savat elementi'
        verbose_name_plural = 'Savat elementlari'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """Subtotal narx"""
        return self.product.price * self.quantity


class Order(models.Model):
    """Buyurtmalar"""
    
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlandi'),
        ('processing', 'Tayyorlanmoqda'),
        ('shipped', 'Jo\'natildi'),
        ('delivered', 'Yetkazildi'),
        ('cancelled', 'Bekor qilindi'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Naqd pul (yetkazib berishda)'),
        ('card', 'Karta orqali'),
        ('payme', 'Payme'),
        ('click', 'Click'),
    ]
    
    # Order ma'lumotlari
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Buyurtma raqami')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='Foydalanuvchi')
    
    # Yetkazib berish ma'lumotlari
    full_name = models.CharField(max_length=200, verbose_name='To\'liq ism')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(blank=True, verbose_name='Email')
    
    address = models.CharField(max_length=255, verbose_name='Manzil')
    city = models.CharField(max_length=100, verbose_name='Shahar')
    region = models.CharField(max_length=100, verbose_name='Viloyat')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Pochta indeksi')
    
    delivery_notes = models.TextField(blank=True, verbose_name='Yetkazib berish haqida izoh')
    
    # To'lov ma'lumotlari
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='To\'lov usuli')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Jami (mahsulotlar)')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Yetkazib berish narxi')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Chegirma')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Jami to\'lov')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Holat')
    is_paid = models.BooleanField(default=False, verbose_name='To\'langan')
    
    # Sanalar
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tasdiqlangan vaqt')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Yetkazilgan vaqt')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
    
    def __str__(self):
        return f"Buyurtma #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import random
            import string
            while True:
                order_num = 'ORD' + ''.join(random.choices(string.digits, k=10))
                if not Order.objects.filter(order_number=order_num).exists():
                    self.order_number = order_num
                    break
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Buyurtmadagi mahsulot"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Buyurtma')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Mahsulot')
    
    product_name = models.CharField(max_length=200, verbose_name='Mahsulot nomi')  # Snapshot
    product_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Mahsulot narxi')  # Snapshot
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Miqdor')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Jami')
    
    class Meta:
        verbose_name = 'Buyurtma elementi'
        verbose_name_plural = 'Buyurtma elementlari'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Create snapshot of product info
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_price:
            self.product_price = self.product.price
        if not self.subtotal:
            self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """Foydalanuvchi sevimli mahsulotlari"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist', verbose_name='Foydalanuvchi')
    products = models.ManyToManyField(Product, related_name='wishlisted_by', verbose_name='Mahsulotlar')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sevimlilar'
        verbose_name_plural = 'Sevimlilar'
    
    def __str__(self):
        return f"{self.user.username} sevimlilari"

