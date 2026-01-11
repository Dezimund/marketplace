from django.db.models import Count, Avg, Q, F
from django.db.models.functions import Coalesce
from decimal import Decimal
import random


class RecommendationEngine:

    def __init__(self, product_model, order_item_model, review_model=None):
        self.Product = product_model
        self.OrderItem = order_item_model
        self.Review = review_model

    def get_similar_products(self, product, limit=8):
        price_range = Decimal('0.3')
        min_price = product.price * (1 - price_range)
        max_price = product.price * (1 + price_range)

        queryset = self.Product.objects.filter(
            category=product.category,
        ).exclude(
            id=product.id
        )

        same_color = queryset.filter(color__iexact=product.color) if product.color else queryset.none()

        similar_price = queryset.filter(
            price__gte=min_price,
            price__lte=max_price
        )

        results = list(same_color[:limit // 2])
        remaining = limit - len(results)

        for p in similar_price.exclude(id__in=[r.id for r in results])[:remaining]:
            results.append(p)

        if len(results) < limit:
            remaining = limit - len(results)
            for p in queryset.exclude(id__in=[r.id for r in results])[:remaining]:
                results.append(p)

        return results

    def get_also_bought(self, product, limit=6):
        orders_with_product = self.OrderItem.objects.filter(
            product=product
        ).values_list('order_id', flat=True)

        also_bought = self.OrderItem.objects.filter(
            order_id__in=orders_with_product
        ).exclude(
            product=product
        ).values('product').annotate(
            count=Count('product')
        ).order_by('-count')[:limit]

        product_ids = [item['product'] for item in also_bought]

        return self.Product.objects.filter(id__in=product_ids)

    def get_users_also_viewed(self, product, user=None, limit=6):
        return self.Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        ).order_by('-views_count')[:limit]


    def get_trending(self, days=7, limit=12):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Value, IntegerField
        from django.db.models.functions import Coalesce

        since = timezone.now() - timedelta(days=days)

        trending = self.Product.objects.annotate(
            recent_sales=Coalesce(
                Count(
                    'orderitem',
                    filter=Q(orderitem__order__created_at__gte=since)
                ),
                Value(0),
                output_field=IntegerField()
            )
        ).annotate(
            trend_score=F('recent_sales') * 3 + F('views_count')
        ).order_by('-trend_score')[:limit]

        return trending

    def get_bestsellers(self, limit=12):
        return self.Product.objects.annotate(
            total_sales=Count('orderitem')
        ).order_by('-total_sales')[:limit]

    def get_top_rated(self, min_reviews=3, limit=12):
        if not self.Review:
            return self.Product.objects.none()

        return self.Product.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(
            review_count__gte=min_reviews
        ).order_by('-avg_rating', '-review_count')[:limit]


    def get_for_user(self, user, limit=12):
        if not user or not user.is_authenticated:
            return self.get_trending(limit=limit)

        purchased_categories = self.OrderItem.objects.filter(
            order__user=user
        ).values_list('product__category_id', flat=True).distinct()

        from django.db.models import Avg as DjangoAvg
        avg_price = self.OrderItem.objects.filter(
            order__user=user
        ).aggregate(avg=DjangoAvg('product__price'))['avg'] or Decimal('500')

        price_range = Decimal('0.5')
        min_price = avg_price * (1 - price_range)
        max_price = avg_price * (1 + price_range)

        purchased_products = self.OrderItem.objects.filter(
            order__user=user
        ).values_list('product_id', flat=True)

        recommendations = self.Product.objects.filter(
            category_id__in=purchased_categories,
            price__gte=min_price,
            price__lte=max_price
        ).exclude(
            id__in=purchased_products
        )

        if self.Review:
            recommendations = recommendations.annotate(
                avg_rating=Coalesce(Avg('reviews__rating'), Decimal('0'))
            ).order_by('-avg_rating', '-views_count')
        else:
            recommendations = recommendations.order_by('-views_count')

        results = list(recommendations[:limit])

        if len(results) < limit:
            trending = self.get_trending(limit=limit - len(results))
            for p in trending:
                if p not in results and p.id not in purchased_products:
                    results.append(p)

        return results


    def get_cross_sell(self, cart_products, limit=4):
        if not cart_products:
            return self.get_trending(limit=limit)

        cart_categories = [p.category_id for p in cart_products]
        cart_ids = [p.id for p in cart_products]

        cross_sell = self.OrderItem.objects.filter(
            order__items__product_id__in=cart_ids
        ).exclude(
            product_id__in=cart_ids
        ).exclude(
            product__category_id__in=cart_categories
        ).values('product').annotate(
            count=Count('product')
        ).order_by('-count')[:limit]

        product_ids = [item['product'] for item in cross_sell]

        if product_ids:
            return self.Product.objects.filter(id__in=product_ids)

        return self.Product.objects.exclude(
            category_id__in=cart_categories
        ).order_by('-views_count')[:limit]

    def get_upsell(self, product, limit=4):
        return self.Product.objects.filter(
            category=product.category,
            price__gt=product.price
        ).exclude(
            id=product.id
        ).order_by('price')[:limit]