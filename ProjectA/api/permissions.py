from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'seller'):
            return obj.seller == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class IsSellerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
                request.user and
                request.user.is_authenticated and
                (request.user.is_seller or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'seller'):
            return obj.seller == request.user or request.user.is_staff

        return request.user.is_staff


class IsSeller(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                (request.user.is_seller or request.user.is_staff)
        )


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff