from django.db import models
from django.conf import settings
from main.models import Product, ProductSize


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    PAYMENT_PROVIDER_CHOICES = (
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('privat24', 'Privat24'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='User'
    )
    first_name = models.CharField('First name', max_length=50)
    last_name = models.CharField('Last name', max_length=50)
    email = models.EmailField('Email', max_length=254)
    company = models.CharField('Company', max_length=100, blank=True, null=True)
    address1 = models.CharField('Address 1', max_length=255, blank=True, null=True)
    address2 = models.CharField('Address 2', max_length=255, blank=True, null=True)
    city = models.CharField('City', max_length=100, blank=True, null=True)
    country = models.CharField('Country', max_length=100, blank=True, null=True)
    state = models.CharField('State', max_length=100, blank=True, null=True)
    postal_code = models.CharField('Postal code', max_length=20, blank=True, null=True)
    phone_number = models.CharField('Phone number', max_length=20, blank=True, null=True)
    special_instructions = models.TextField('Special instructions', blank=True)
    total_price = models.DecimalField('Total price', max_digits=10, decimal_places=2)
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_provider = models.CharField(
        'Payment provider',
        max_length=20,
        choices=PAYMENT_PROVIDER_CHOICES,
        null=True,
        blank=True
    )
    stripe_payment_intent_id = models.CharField(
        'Stripe Payment Intent ID',
        max_length=255,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField('Created_at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated_at', auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.email}"

    def get_items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Orders'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product'
    )
    size = models.ForeignKey(
        ProductSize,
        on_delete=models.CASCADE,
        verbose_name='Size',
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField('Quantity')
    price = models.DecimalField('Price', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item in order'
        verbose_name_plural = 'Items in order'

    def __str__(self):
        size_name = self.size.size.name if self.size else 'no size'
        return f"{self.product.name} - {size_name} ({self.quantity})"

    def get_total_price(self):
        return self.price * self.quantity