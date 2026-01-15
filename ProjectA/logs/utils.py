from .models import ActionLog


def log_action(request, action_type, obj=None, description='', extra_data=None,
               is_success=True, error_message=''):

    if isinstance(action_type, str):
        action_type = getattr(ActionLog.ActionType, action_type.upper(), ActionLog.ActionType.OTHER)

    return ActionLog.log(
        action_type=action_type,
        request=request,
        obj=obj,
        description=description,
        extra_data=extra_data,
        is_success=is_success,
        error_message=error_message
    )


def log_product_action(request, action, product, extra_data=None):

    action_map = {
        'create': (ActionLog.ActionType.PRODUCT_CREATE, f'Created product "{product.name}"'),
        'update': (ActionLog.ActionType.PRODUCT_UPDATE, f'Updated product "{product.name}"'),
        'delete': (ActionLog.ActionType.PRODUCT_DELETE, f'Deleted product "{product.name}"'),
        'view': (ActionLog.ActionType.PRODUCT_VIEW, f'Reviewed product "{product.name}"'),
    }

    action_type, description = action_map.get(action, (ActionLog.ActionType.OTHER, ''))

    return ActionLog.log(
        action_type=action_type,
        request=request,
        obj=product,
        description=description,
        extra_data=extra_data or {}
    )


def log_cart_action(request, action, cart_item=None, extra_data=None):

    action_map = {
        'add': ActionLog.ActionType.CART_ADD,
        'update': ActionLog.ActionType.CART_UPDATE,
        'remove': ActionLog.ActionType.CART_REMOVE,
        'clear': ActionLog.ActionType.CART_CLEAR,
    }

    action_type = action_map.get(action, ActionLog.ActionType.OTHER)

    if cart_item and hasattr(cart_item, 'product'):
        description = f'{action.capitalize()}: {cart_item.product.name}'
    else:
        description = f'Action with cart: {action}'

    return ActionLog.log(
        action_type=action_type,
        request=request,
        obj=cart_item,
        description=description,
        extra_data=extra_data or {}
    )


def log_order_action(request, action, order, extra_data=None):

    action_map = {
        'create': (ActionLog.ActionType.ORDER_CREATE, f'Created order #{order.id}'),
        'update': (ActionLog.ActionType.ORDER_UPDATE, f'Updated order #{order.id}'),
        'cancel': (ActionLog.ActionType.ORDER_CANCEL, f'Cancelled order #{order.id}'),
    }

    action_type, description = action_map.get(action, (ActionLog.ActionType.OTHER, ''))

    return ActionLog.log(
        action_type=action_type,
        request=request,
        obj=order,
        description=description,
        extra_data=extra_data or {'total': str(order.total) if hasattr(order, 'total') else None}
    )


def log_review_action(request, action, review, extra_data=None):

    action_map = {
        'create': ActionLog.ActionType.REVIEW_CREATE,
        'update': ActionLog.ActionType.REVIEW_UPDATE,
        'delete': ActionLog.ActionType.REVIEW_DELETE,
    }

    action_type = action_map.get(action, ActionLog.ActionType.OTHER)
    product_name = review.product.name if hasattr(review, 'product') else 'Unknown'

    return ActionLog.log(
        action_type=action_type,
        request=request,
        obj=review,
        description=f'Review on "{product_name}"',
        extra_data=extra_data or {'rating': review.rating if hasattr(review, 'rating') else None}
    )


def log_auth_action(request, action, user=None, is_success=True, error_message=''):

    action_map = {
        'login': ActionLog.ActionType.LOGIN,
        'logout': ActionLog.ActionType.LOGOUT,
        'register': ActionLog.ActionType.REGISTER,
        'password_change': ActionLog.ActionType.PASSWORD_CHANGE,
    }

    action_type = action_map.get(action, ActionLog.ActionType.OTHER)

    return ActionLog.log(
        action_type=action_type,
        request=request,
        user=user,
        description=f'{action.capitalize()} {"Successfully" if is_success else "Unsuccess"}',
        is_success=is_success,
        error_message=error_message
    )