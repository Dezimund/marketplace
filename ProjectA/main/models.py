from django.db import models
from django.utils.text import slugify
from reviews.models import Review
from django.db.models import Avg, Count, Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    requires_size = models.BooleanField(default=False, verbose_name="Need a size")

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')
    slug = models.CharField(max_length=100, unique=True)
    seller = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE,
                               related_name='products', null=True, blank=True,
                               verbose_name='Seller')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products', verbose_name='Category')
    color = models.CharField(max_length=100, blank=True, verbose_name='Color')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                    blank=True, verbose_name='Old price')
    description = models.TextField(blank=False, verbose_name='Description')
    main_image = models.ImageField(upload_to='products/main/', verbose_name='Main image')
    is_recommended = models.BooleanField(default=False, verbose_name='Recommended')
    is_bestseller = models.BooleanField(default=False, verbose_name='Bestseller')
    is_new = models.BooleanField(default=True, verbose_name='New')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Views count')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated')
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0, verbose_name='Rating')
    reviews_count = models.PositiveIntegerField(default=0, verbose_name='Quantity of reviews')
    stock = models.PositiveIntegerField(default=0,verbose_name='Quantity in warehouse')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int(100 - (self.price / self.old_price * 100))
        return 0

    def update_rating(self):
        stats = self.reviews.filter(is_approved=True).aggregate(
            avg_rating = Avg('rating'),
            count = Count('id')
        )
        self.rating = stats['avg_rating'] or 0
        self.reviews_count = stats['count']
        self.save(update_fields=['rating', 'reviews_count'])

    def update_stock_from_sizes(self):
        if self.category and self.category.requires_size:
            total_stock = self.product_sizes.aggregate(
                total=Sum('stock')
            )['total'] or 0
            self.stock = total_stock
            self.save(update_fields=['stock'])


class ProductSize(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                related_name='product_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0, verbose_name='On stock')

    class Meta:
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'

    def __str__(self):
        return f"{self.size.name} ({self.stock} pcs.) for {self.product.name}"

@receiver(post_save, sender=ProductSize)
def update_product_stock_on_save(sender, instance, **kwargs):
    if instance.product.category and instance.product.category.requires_size:
        total_stock = instance.product.product_sizes.aggregate(
            total=Sum('stock')
        )['total'] or 0
        Product.objects.filter(pk=instance.product.pk).update(stock=total_stock)

@receiver(post_delete, sender=ProductSize)
def update_product_stock_on_delete(sender, instance, **kwargs):
    try:
        if instance.product.category and instance.product.category.requires_size:
            total_stock = instance.product.product_sizes.aggregate(
                total=Sum('stock')
            )['total'] or 0
            Product.objects.filter(pk=instance.product.pk).update(stock=total_stock)
    except Product.DoesNotExist:
        pass


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images')
    image = models.ImageField(upload_to='products/extra/', verbose_name='image')

    class Meta:
        verbose_name = 'Save product'
        verbose_name_plural = 'Save products'