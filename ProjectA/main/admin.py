from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductSize, ProductImage, Size


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'requires_size', 'products_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'category', 'price', 'old_price',
        'stock', 'stock_status', 'is_recommended', 'is_bestseller',
        'is_new', 'views_count', 'created_at'
    )
    list_display_links = ('id', 'name')
    list_filter = (
        'category', 'is_recommended', 'is_bestseller',
        'is_new', 'seller', 'created_at'
    )
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'preview_image')
    list_editable = ('stock', 'is_recommended', 'is_bestseller', 'is_new')
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [ProductImageInline, ProductSizeInline]

    fieldsets = (
        ('Main info', {
            'fields': ('name', 'slug', 'seller', 'category', 'description')
        }),
        ('Price', {
            'fields': ('price', 'old_price')
        }),
        ('Stock', {
            'fields': ('stock', 'color'),
            'description': 'Quantity 0 = no in stock'
        }),
        ('Images', {
            'fields': ('main_image', 'preview_image')
        }),
        ('Marks', {
            'fields': ('is_recommended', 'is_bestseller', 'is_new')
        }),
        ('Rating', {
            'fields': ('rating', 'reviews_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def stock_status(self, obj):
        if obj.stock > 10:
            color = 'green'
            text = f'In stock ({obj.stock})'
        elif obj.stock > 0:
            color = 'orange'
            text = f'Few ({obj.stock})'
        else:
            color = 'red'
            text = 'Out of stock'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )

    def stock_info(self, obj):
        if obj.category and obj.category.requires_size:
            sizes_info = []
            for ps in obj.product_sizes.select_related('size').all():
                sizes_info.append(f"{ps.size.name}: {ps.stock} pcs.")
            if sizes_info:
                from django.db.models import Sum
                total = obj.product_sizes.aggregate(total=Sum('stock'))['total'] or 0
                return format_html(
                    '<div style="line-height: 1.8;">{}<br><strong>Total: {} pcs.</strong></div>',
                    '<br>'.join(sizes_info),
                    total
                )
            return 'Sizes dont add'
        else:
            stock = getattr(obj, 'stock', 0) or 0
            return f'{stock} pcs.'

    stock_info.short_description = 'Quantity in warehouse'

    stock_status.short_description = 'Status'
    stock_status.admin_order_field = 'stock'

    def preview_image(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.main_image.url
            )
        return '-'

    preview_image.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        if not obj.seller_id:
            obj.seller = request.user
        super().save_model(request, obj, form, change)

    actions = ['make_in_stock', 'make_out_of_stock', 'mark_as_bestseller', 'mark_as_recommended']

    @admin.action(description='Stock 10 pcs.)')
    def make_in_stock(self, request, queryset):
        queryset.update(stock=10)
        self.message_user(request, f'{queryset.count()} products updated')

    @admin.action(description='Out of stock')
    def make_out_of_stock(self, request, queryset):
        queryset.update(stock=0)
        self.message_user(request, f'{queryset.count()} products updated')

    @admin.action(description='Mark as bestseller')
    def mark_as_bestseller(self, request, queryset):
        queryset.update(is_bestseller=True)
        self.message_user(request, f'{queryset.count()} products as bestseller')

    @admin.action(description='Mark as recommended')
    def mark_as_recommended(self, request, queryset):
        queryset.update(is_recommended=True)
        self.message_user(request, f'{queryset.count()} products as recommended')


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock')
    list_filter = ('size', 'product__category')
    search_fields = ('product__name',)
    list_editable = ('stock',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'preview')
    list_filter = ('product__category',)
    search_fields = ('product__name',)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />',
                obj.image.url
            )
        return '-'

    preview.short_description = 'Preview'