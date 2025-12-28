from django.contrib import admin
from django.shortcuts import redirect
from .models import Category, Size, Product, ProductImage, ProductSize
from django.contrib import messages


class ProductImageInLine(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSizeInLine(admin.TabularInline):
    model = ProductSize
    extra = 1
    min_num = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'old_price', 'is_recommended',
                    'is_bestseller', 'is_new', 'views_count', 'created_at']
    list_filter = ['category', 'is_recommended', 'is_bestseller', 'is_new', 'color']
    search_fields = ['name', 'color', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_recommended', 'is_bestseller', 'is_new']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    inlines = [ProductImageInLine, ProductSizeInLine]

    fieldsets = (
        ('General info', {
            'fields': ('name', 'slug', 'category', 'seller', 'description')
        }),
        ('Price', {
            'fields': ('price', 'old_price')
        }),
        ('Images', {
            'fields': ('main_image',)
        }),
        ('Specifies', {
            'fields': ('color',)
        }),
        ('Marketing', {
            'fields': ('is_recommended', 'is_bestseller', 'is_new'),
            'description': 'Choose field to show on main page'
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_recommended', 'remove_recommended',
               'make_bestseller', 'remove_bestseller']

    @admin.action(description='Mark as recommended')
    def make_recommended(self, request, queryset):
        updated = queryset.update(is_recommended=True)
        self.message_user(request, f'{updated} products marked as recommended.')

    @admin.action(description='Remove from recommended')
    def remove_recommended(self, request, queryset):
        updated = queryset.update(is_recommended=False)
        self.message_user(request, f'{updated} products removed from recommended.')

    @admin.action(description='Mark as bestseller')
    def make_bestseller(self, request, queryset):
        updated = queryset.update(is_bestseller=True)
        self.message_user(request, f'{updated} products marked as bestseller.')

    @admin.action(description='Remove from bestseller')
    def remove_bestseller(self, request, queryset):
        updated = queryset.update(is_bestseller=False)
        self.message_user(request, f'{updated} products removed from bestseller.')

    def response_add(self, request, obj, post_url_continue=None):
        if obj.category.requires_size and not obj.product_sizes.exists():
            messages.warning(
                request,
                f'Category "{obj.category.name}" need size. '
                f'Please add size for the Product "{obj.name}".'
            )
            return redirect('admin:main_product_change', obj.pk)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if obj.category.requires_size and not obj.product_sizes.exists():
            messages.error(
                request,
                f'Category "{obj.category.name}" need size. '
                f'Product "{obj.name}" cannot be saved without size.'
            )
            return redirect('admin:main_product_change', obj.pk)
        return super().response_change(request, obj)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'requires_size', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['requires_size']

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = 'Quantity of products'


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']