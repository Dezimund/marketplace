from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.views.generic import View
from .forms import OrderForm
from .models import Order, OrderItem
from cart.views import CartMixin
from cart.models import Cart
from main.models import ProductSize
from django.shortcuts import get_object_or_404
from decimal import Decimal


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class CheckoutView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)

        if cart.total_items == 0:
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/empty_cart.html', {'message': 'Ваш кошик порожній'})
            return redirect('cart:cart_modal')

        total_price = cart.subtotal

        form = OrderForm(user=request.user)
        context = {
            'form': form,
            'cart': cart,
            'cart_items': cart.items.select_related('product', 'product_size__size').order_by('added_at'),
            'total_price': total_price,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        cart = self.get_cart(request)
        payment_provider = request.POST.get('payment_provider')

        if cart.total_items == 0:
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/empty_cart.html', {'message': 'Ваш кошик порожній'})
            return redirect('cart:cart_modal')

        total_price = cart.subtotal
        form_data = request.POST.copy()
        if not form_data.get('email'):
            form_data['email'] = request.user.email
        form = OrderForm(form_data, user=request.user)

        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                company=form.cleaned_data.get('company', ''),
                address1=form.cleaned_data.get('address1', ''),
                address2=form.cleaned_data.get('address2', ''),
                city=form.cleaned_data.get('city', ''),
                country=form.cleaned_data.get('country', ''),
                state=form.cleaned_data.get('state', ''),
                postal_code=form.cleaned_data.get('postal_code', ''),
                phone_number=form.cleaned_data.get('phone_number', ''),
                special_instructions='',
                total_price=total_price,
                payment_provider=payment_provider,
            )

            for item in cart.items.select_related('product', 'product_size__size'):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.product_size,
                    quantity=item.quantity,
                    price=item.product.price or Decimal('0.00')
                )

            cart.items.all().delete()

            context = {
                'order': order,
                'message': 'Замовлення успішно створено!'
            }

            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/order_success.html', context)
            return render(request, 'orders/order_success.html', context)

        context = {
            'form': form,
            'cart': cart,
            'cart_items': cart.items.select_related('product', 'product_size__size').order_by('added_at'),
            'total_price': total_price,
            'errors': form.errors,
        }
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class OrderHistoryView(View):

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        context = {
            'orders': orders,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/order_history_content.html', context)
        return render(request, 'orders/order_history.html', context)


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class OrderDetailView(View):

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        context = {
            'order': order,
            'items': order.items.select_related('product', 'size__size'),
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/order_detail_content.html', context)
        return render(request, 'orders/order_detail.html', context)