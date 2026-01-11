from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('image_preview', 'product', 'size', 'quantity', 'price', 'get_total_price')
    readonly_fields = ('image_preview', 'get_total_price')
    can_delete = False

    def image_preview(self, obj):
        if obj.product.main_image:
            return mark_safe(
                f'<img src="{obj.product.main_image.url}" '
                f'style="max-height: 50px; max-width: 50px; object-fit: cover;" />'
            )
        return mark_safe('<span style="color: gray;">No image</span>')

    image_preview.short_description = 'Фото'

    def get_total_price(self, obj):
        try:
            return f"{obj.get_total_price()} ₴"
        except (TypeError, AttributeError):
            return mark_safe('<span style="color: red;">Error</span>')

    get_total_price.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'email', 'total_price',
        'payment_provider', 'status', 'created_at'
    )
    list_filter = ('status', 'payment_provider', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'id')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'total_price', 'stripe_payment_intent_id')
    inlines = [OrderItemInLine]

    list_per_page = 25

    fieldsets = (
        ('Info aboout order', {
            'fields': (
                'user', 'first_name', 'last_name', 'email',
                'company', 'address1', 'address2', 'city',
                'country', 'state', 'postal_code',
                'phone_number', 'special_instructions', 'total_price'
            )
        }),
        ('Payment and status', {
            'fields': ('status', 'payment_provider', 'stripe_payment_intent_id',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + (
                'user', 'first_name', 'last_name', 'email',
                'company', 'address1', 'address2', 'city',
                'country', 'state', 'postal_code', 'phone_number'
            )
        return self.readonly_fields


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'size', 'quantity', 'price', 'get_total')
    list_filter = ('order__status',)
    search_fields = ('product__name', 'order__id')

    def get_total(self, obj):
        return f"{obj.get_total_price()} ₴"

    get_total.short_description = 'Total'