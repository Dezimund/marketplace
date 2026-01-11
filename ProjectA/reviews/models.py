from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Review(models.Model):

    product = models.ForeignKey(
        'main.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Product'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='User'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Mark'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Title'
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Text review'
    )
    advantages = models.TextField(
        blank=True,
        default='',
        verbose_name='Advantages'
    )
    disadvantages = models.TextField(
        blank=True,
        default='',
        verbose_name='Disadvantages'
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name='Confirmed order'
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name='Approved'
    )
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Useful'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated'
    )

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}★)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()


class ReviewHelpful(models.Model):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name='Review'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name='User'
    )
    is_helpful = models.BooleanField(
        default=True,
        verbose_name='Useful'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Vote for review'
        verbose_name_plural = 'Votes for reviews'
        unique_together = ['review', 'user']