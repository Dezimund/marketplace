from django.contrib import admin
from .models import Cart, CartItem


class CartItemInLine(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price', 'size_display')

    def size_display(self, obj):
        return obj.product_size.size.name if obj.product_size else "No Size"

    size_display.short_description = "Size"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'total_items', 'subtotal', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('session_key',)
    inlines = [CartItemInLine]
    readonly_fields = ('total_items', 'subtotal')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'size_display', 'quantity', 'total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__name', 'cart__session_key')
    readonly_fields = ('total_price',)

    def size_display(self, obj):
        return obj.product_size.size.name if obj.product_size else "No Size"

    size_display.short_description = "Size"