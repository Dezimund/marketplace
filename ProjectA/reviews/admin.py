from django.contrib import admin
from .models import Review, ReviewHelpful


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product', 'user', 'rating', 'title',
        'is_verified_purchase', 'is_approved', 'helpful_count', 'created_at'
    )
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'text')
    readonly_fields = ('created_at', 'updated_at', 'helpful_count')
    list_editable = ('is_approved',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Main', {
            'fields': ('product', 'user', 'rating')
        }),
        ('Text of review', {
            'fields': ('title', 'text', 'advantages', 'disadvantages')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_approved', 'helpful_count')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.product.update_rating()


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')