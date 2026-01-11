from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from main.models import Product
from orders.models import OrderItem
from .engine import RecommendationEngine
from api.serializers import ProductListSerializer
from cart.models import Cart


def get_models():
    try:
        from reviews.models import Review
    except ImportError:
        Review = None
    return Product, OrderItem, Review


def get_engine():
    Product, OrderItem, Review = get_models()
    return RecommendationEngine(Product, OrderItem, Review)


def get_serializer():
    return ProductListSerializer


class RecommendationsAPIView(APIView):

    def get(self, request):
        engine = get_engine()
        Product, OrderItem, Review = get_models()
        ProductListSerializer = get_serializer()

        rec_type = request.query_params.get('type', 'trending')
        product_slug = request.query_params.get('product')
        limit = min(int(request.query_params.get('limit', 12)), 50)  # Max 50
        days = int(request.query_params.get('days', 7))

        products = []

        try:
            if rec_type == 'trending':
                products = engine.get_trending(days=days, limit=limit)

            elif rec_type == 'for_user':
                if not request.user.is_authenticated:
                    products = engine.get_trending(days=days, limit=limit)
                else:
                    products = engine.get_for_user(request.user, limit=limit)

            elif rec_type == 'similar':
                if not product_slug:
                    return Response(
                        {'error': 'Параметр product обов\'язковий'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                product = get_object_or_404(Product, slug=product_slug)
                products = engine.get_similar_products(product, limit=limit)

            elif rec_type == 'also_bought':
                if not product_slug:
                    return Response(
                        {'error': 'Параметр product обов\'язковий'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                product = get_object_or_404(Product, slug=product_slug)
                products = engine.get_also_bought(product, limit=limit)

            elif rec_type == 'top_rated':
                min_reviews = int(request.query_params.get('min_reviews', 3))
                products = engine.get_top_rated(min_reviews=min_reviews, limit=limit)

            elif rec_type == 'bestsellers':
                products = engine.get_bestsellers(limit=limit)

            elif rec_type == 'upsell':
                if not product_slug:
                    return Response(
                        {'error': 'Параметр product обов\'язковий'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                product = get_object_or_404(Product, slug=product_slug)
                products = engine.get_upsell(product, limit=limit)

            elif rec_type == 'cross_sell':
                cart_products = []

                if request.session.session_key:
                    try:
                        cart = Cart.objects.get(session_key=request.session.session_key)
                        cart_products = [item.product for item in cart.items.all()]
                    except Cart.DoesNotExist:
                        pass

                products = engine.get_cross_sell(cart_products, limit=limit)

            else:
                products = engine.get_trending(limit=limit)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = ProductListSerializer(products, many=True)

        return Response({
            'type': rec_type,
            'count': len(serializer.data),
            'products': serializer.data
        })


class PersonalizedHomeAPIView(APIView):

    def get(self, request):
        engine = get_engine()
        Product, OrderItem, Review = get_models()
        ProductListSerializer = get_serializer()

        blocks = []

        if request.user.is_authenticated:
            personal = engine.get_for_user(request.user, limit=8)
            if personal:
                blocks.append({
                    'title': 'Рекомендовано для вас',
                    'type': 'for_user',
                    'products': ProductListSerializer(personal, many=True).data
                })

        trending = engine.get_trending(days=7, limit=8)
        blocks.append({
            'title': 'Популярне зараз',
            'type': 'trending',
            'products': ProductListSerializer(trending, many=True).data
        })

        new_products = Product.objects.filter(is_new=True).order_by('-created_at')[:8]
        blocks.append({
            'title': 'Новинки',
            'type': 'new',
            'products': ProductListSerializer(new_products, many=True).data
        })

        bestsellers = engine.get_bestsellers(limit=8)
        blocks.append({
            'title': 'Бестселери',
            'type': 'bestsellers',
            'products': ProductListSerializer(bestsellers, many=True).data
        })

        if Review:
            top_rated = engine.get_top_rated(min_reviews=2, limit=8)
            if top_rated:
                blocks.append({
                    'title': 'Найкраще оцінені',
                    'type': 'top_rated',
                    'products': ProductListSerializer(top_rated, many=True).data
                })

        return Response({'blocks': blocks})