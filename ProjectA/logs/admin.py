from django.contrib import admin
from .models import ActionLog


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):

    list_display = [
        'created_at',
        'user',
        'action_type',
        'object_type',
        'object_repr',
        'ip_address',
        'is_success'
    ]
    list_filter = [
        'action_type',
        'is_success',
        'created_at',
        'object_type'
    ]
    search_fields = [
        'user__email',
        'description',
        'object_repr',
        'ip_address'
    ]
    readonly_fields = [
        'user',
        'action_type',
        'description',
        'object_type',
        'object_id',
        'object_repr',
        'extra_data',
        'ip_address',
        'user_agent',
        'is_success',
        'error_message',
        'created_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Main information', {
            'fields': ('user', 'action_type', 'description', 'created_at')
        }),
        ('Object', {
            'fields': ('object_type', 'object_id', 'object_repr')
        }),
        ('Request', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_success', 'error_message')
        }),
        ('Additional information', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser