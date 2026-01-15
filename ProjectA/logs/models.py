from django.db import models
from django.conf import settings


class ActionLog(models.Model):

    class ActionType(models.TextChoices):
        LOGIN = 'login'
        LOGOUT = 'logout'
        REGISTER = 'register'
        PASSWORD_CHANGE = 'password_change'

        PRODUCT_CREATE = 'product_create'
        PRODUCT_UPDATE = 'product_update'
        PRODUCT_DELETE = 'product_delete'
        PRODUCT_VIEW = 'product_view'

        CART_ADD = 'cart_add'
        CART_UPDATE = 'cart_update'
        CART_REMOVE = 'cart_remove'
        CART_CLEAR = 'cart_clear'

        ORDER_CREATE = 'order_create'
        ORDER_UPDATE = 'order_update'
        ORDER_CANCEL = 'order_cancel'

        REVIEW_CREATE = 'review_create'
        REVIEW_UPDATE = 'review_update'
        REVIEW_DELETE = 'review_delete'

        PROFILE_UPDATE = 'profile_update'

        OTHER = 'other'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='action_logs',
        verbose_name='User'
    )
    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        verbose_name='Action type'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Action description'
    )

    object_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Object type'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Object ID'
    )
    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Object representation'
    )

    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Additional information'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP address'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )

    is_success = models.BooleanField(
        default=True,
        verbose_name='Successfully'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Error'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Time of action'
    )

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{user_str} - {self.get_action_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def log(cls, action_type, request=None, user=None, description='',
            obj=None, extra_data=None, is_success=True, error_message=''):

        log_entry = cls(
            action_type=action_type,
            description=description,
            is_success=is_success,
            error_message=error_message,
            extra_data=extra_data or {}
        )

        if user:
            log_entry.user = user
        elif request and request.user.is_authenticated:
            log_entry.user = request.user

        if request:
            log_entry.ip_address = cls._get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        if obj:
            log_entry.object_type = obj.__class__.__name__
            log_entry.object_id = obj.pk
            log_entry.object_repr = str(obj)[:255]

        log_entry.save()
        return log_entry

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')