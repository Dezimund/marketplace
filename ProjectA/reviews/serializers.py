from rest_framework import serializers
from .models import Review, ReviewHelpful
from orders.models import OrderItem


class ReviewUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'first_name': instance.first_name or '',
            'last_name': instance.last_name[:1] + '.' if instance.last_name else '',  # Тільки перша буква прізвища
        }


class ReviewListSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'rating', 'title', 'text',
            'advantages', 'disadvantages', 'is_verified_purchase',
            'helpful_count', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified_purchase', 'helpful_count', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'text', 'advantages', 'disadvantages']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Оцінка має бути від 1 до 5')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        product = self.context['product']

        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError(
                {'detail': 'Ви вже залишили відгук на цей товар'}
            )


        is_verified = OrderItem.objects.filter(
            order__user=user,
            order__status='delivered',
            product=product
        ).exists()

        review = Review.objects.create(
            product=product,
            user=user,
            is_verified_purchase=is_verified,
            **validated_data
        )
        return review


class ReviewDetailSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    is_own = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'rating', 'title', 'text',
            'advantages', 'disadvantages', 'is_verified_purchase',
            'helpful_count', 'created_at', 'is_own', 'user_vote'
        ]

    def get_is_own(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = ReviewHelpful.objects.filter(
                review=obj, user=request.user
            ).first()
            if vote:
                return 'helpful' if vote.is_helpful else 'not_helpful'
        return None


class ReviewStatsSerializer(serializers.Serializer):
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()
    verified_purchases_percent = serializers.FloatField()