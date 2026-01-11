from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Q

from main.models import Product
from .models import Review, ReviewHelpful
from .serializers import (ReviewListSerializer, ReviewCreateSerializer, ReviewDetailSerializer, ReviewStatsSerializer,)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        queryset = Review.objects.filter(is_approved=True)

        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)

        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)

        verified_only = self.request.query_params.get('verified_only')
        if verified_only == 'true':
            queryset = queryset.filter(is_verified_purchase=True)

        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'helpful':
            queryset = queryset.order_by('-helpful_count', '-created_at')
        elif ordering == 'rating_high':
            queryset = queryset.order_by('-rating', '-created_at')
        elif ordering == 'rating_low':
            queryset = queryset.order_by('rating', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset.select_related('user', 'product')

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return ReviewDetailSerializer
        return ReviewListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_slug = self.kwargs.get('product_slug')
        if product_slug:
            context['product'] = get_object_or_404(Product, slug=product_slug)
        return context

    def create(self, request, product_slug=None):
        product = get_object_or_404(Product, slug=product_slug)

        serializer = self.get_serializer(data=request.data)
        serializer.context['product'] = product

        if serializer.is_valid():
            review = serializer.save()
            return Response(
                ReviewDetailSerializer(review, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        review = self.get_object()

        if review.user != request.user:
            return Response(
                {'detail': 'Ви можете редагувати тільки свої відгуки'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()

        if review.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'Ви можете видаляти тільки свої відгуки'},
                status=status.HTTP_403_FORBIDDEN
            )

        product = review.product
        response = super().destroy(request, *args, **kwargs)
        product.update_rating()
        return response

    @action(detail=False, methods=['get'])
    def stats(self, request, product_slug=None):
        product = get_object_or_404(Product, slug=product_slug)
        reviews = Review.objects.filter(product=product, is_approved=True)

        distribution = reviews.values('rating').annotate(
            count=Count('id')
        ).order_by('rating')

        rating_dist = {str(i): 0 for i in range(1, 6)}
        for item in distribution:
            rating_dist[str(item['rating'])] = item['count']

        total = reviews.count()
        verified_count = reviews.filter(is_verified_purchase=True).count()

        stats = {
            'average_rating': float(product.rating) if hasattr(product, 'rating') else 0,
            'total_reviews': total,
            'rating_distribution': rating_dist,
            'verified_purchases_percent': (verified_count / total * 100) if total > 0 else 0,
        }

        return Response(ReviewStatsSerializer(stats).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def helpful(self, request, pk=None, product_slug=None):
        review = self.get_object()

        if review.user == request.user:
            return Response(
                {'detail': 'Не можна голосувати за свій відгук'},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_helpful = request.data.get('is_helpful', True)

        vote, created = ReviewHelpful.objects.update_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': is_helpful}
        )

        review.helpful_count = review.helpful_votes.filter(is_helpful=True).count()
        review.save(update_fields=['helpful_count'])

        return Response({
            'helpful_count': review.helpful_count,
            'user_vote': 'helpful' if is_helpful else 'not_helpful'
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request, product_slug=None):
        product = get_object_or_404(Product, slug=product_slug)

        try:
            review = Review.objects.get(product=product, user=request.user)
            return Response(ReviewDetailSerializer(review, context={'request': request}).data)
        except Review.DoesNotExist:
            return Response({'detail': 'Ви ще не залишили відгук'}, status=status.HTTP_404_NOT_FOUND)


class UserReviewsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('product')