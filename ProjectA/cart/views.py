from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.template.response import TemplateResponse
from main.models import ProductSize, Product
from .models import Cart, CartItem
from django.db import transaction
from .forms import AddToCartForm


class CartMixin:
    def get_cart(self, request):
        if hasattr(request, 'cart'):
            return request.cart

        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

        request.session['cart_id'] = cart.id
        request.session.modified = True
        return cart


class CartModalView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size',
                'product_size__size',
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_modal_content.html', context)


class AddToCartView(CartMixin, View):
    @transaction.atomic
    def post(self, request, slug):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, slug=slug)

        form = AddToCartForm(request.POST, product=product)

        if not form.is_valid():
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'cart/cart_error.html', {
                    'error': 'Невірні дані форми',
                    'errors': form.errors,
                })
            return JsonResponse({
                'error': 'Invalid form data',
                'errors': form.errors,
            }, status=400)

        requires_size = product.category.requires_size
        size_id = form.cleaned_data.get('size_id')
        product_size = None

        if size_id:
            product_size = get_object_or_404(
                ProductSize,
                id=size_id,
                product=product,
            )
        elif requires_size:
            product_size = product.product_sizes.filter(stock__gt=0).first()
            if not product_size:
                if request.headers.get('HX-Request'):
                    return TemplateResponse(request, 'cart/cart_error.html', {
                        'error': 'Розмір обов\'язковий, але розміри недоступні'
                    })
                return JsonResponse({
                    'error': 'Size is required but no sizes available'
                }, status=400)

        quantity = form.cleaned_data['quantity']

        if product_size:
            if product_size.stock < quantity:
                error_msg = f'Доступно лише {product_size.stock} шт.'
                if request.headers.get('HX-Request'):
                    return TemplateResponse(request, 'cart/cart_error.html', {
                        'error': error_msg
                    })
                return JsonResponse({'error': error_msg}, status=400)

            existing_item = cart.items.filter(
                product=product,
                product_size=product_size,
            ).first()

            if existing_item:
                total_quantity = existing_item.quantity + quantity
                if total_quantity > product_size.stock:
                    available = product_size.stock - existing_item.quantity
                    error_msg = f"Неможливо додати {quantity} шт. Доступно лише {available} шт."
                    if request.headers.get('HX-Request'):
                        return TemplateResponse(request, 'cart/cart_error.html', {
                            'error': error_msg
                        })
                    return JsonResponse({'error': error_msg}, status=400)

        cart_item = cart.add_product(product, product_size, quantity)

        request.session['cart_id'] = cart.id
        request.session.modified = True

        if request.headers.get('HX-Request'):
            context = {
                'cart': cart,
                'cart_items': cart.items.select_related(
                    'product',
                    'product_size',
                    'product_size__size',
                ).order_by('-added_at'),
                'added_product': product,
                'added_quantity': quantity,
            }
            return TemplateResponse(request, 'cart/cart_modal_content.html', context)

        return JsonResponse({
            'success': True,
            'total_items': cart.total_items,
            'message': f"{product.name} додано до кошика",
            'cart_item_id': cart_item.id,
        })


class UpdateCartItemView(CartMixin, View):
    @transaction.atomic
    def post(self, request, item_id):
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity < 0:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        if quantity == 0:
            cart_item.delete()
        else:
            if cart_item.product_size and quantity > cart_item.product_size.stock:
                error_msg = f'Доступно лише {cart_item.product_size.stock} шт.'
                if request.headers.get('HX-Request'):
                    return TemplateResponse(request, 'cart/cart_error.html', {
                        'error': error_msg
                    })
                return JsonResponse({'error': error_msg}, status=400)

            cart_item.quantity = quantity
            cart_item.save()

        request.session['cart_id'] = cart.id
        request.session.modified = True

        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size',
                'product_size__size',
            ).order_by('-added_at')
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_modal_content.html', context)

        return JsonResponse({
            'success': True,
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal),
        })


class RemoveCartItemView(CartMixin, View):
    def post(self, request, item_id):
        cart = self.get_cart(request)

        try:
            cart_item = cart.items.get(id=item_id)
            product_name = cart_item.product.name
            cart_item.delete()

            request.session['cart_id'] = cart.id
            request.session.modified = True

            context = {
                'cart': cart,
                'cart_items': cart.items.select_related(
                    'product',
                    'product_size',
                    'product_size__size',
                ).order_by('-added_at'),
                'removed_product': product_name,
            }

            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'cart/cart_modal_content.html', context)

            return JsonResponse({
                'success': True,
                'total_items': cart.total_items,
                'subtotal': float(cart.subtotal),
                'message': f'{product_name} видалено з кошика',
            })

        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)


class CartCountView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        return JsonResponse({
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal),
        })


class ClearCartView(CartMixin, View):
    def post(self, request):
        cart = self.get_cart(request)
        cart.clear()

        request.session['cart_id'] = cart.id
        request.session.modified = True

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_empty.html', {
                'cart': cart
            })

        return JsonResponse({
            'success': True,
            'message': 'Кошик очищено'
        })


class CartSummaryView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size',
                'product_size__size',
            ).order_by('-added_at')
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_summary_content.html', context)

        return TemplateResponse(request, 'cart/cart_summary.html', context)