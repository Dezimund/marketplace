from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.template.response import TemplateResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db import transaction
import re

from main.models import Product, Category, Size, ProductSize, ProductImage
from .forms import ProductForm, ProductSizeForm, ProductImageFormSet


def generate_unique_slug(name, model_class):
    slug = slugify(name, lowercase=True, separator='-')

    if not slug:
        slug = 'product'

    base_slug = slug
    counter = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class SellerRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_seller


class SellerProductListView(LoginRequiredMixin, SellerRequiredMixin, View):

    def get(self, request):
        products = Product.objects.filter(seller=request.user).order_by('-created_at')

        context = {
            'products': products,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'seller/product_list_content.html', context)
        return render(request, 'seller/product_list.html', context)


class SellerProductCreateView(LoginRequiredMixin, SellerRequiredMixin, View):

    def get(self, request):
        form = ProductForm()
        categories = Category.objects.all()
        sizes = Size.objects.all()

        context = {
            'form': form,
            'categories': categories,
            'sizes': sizes,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'seller/product_form_content.html', context)
        return render(request, 'seller/product_form.html', context)

    @transaction.atomic
    def post(self, request):
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user

            product.slug = generate_unique_slug(product.name, Product)

            product.save()

            main_image = request.FILES.get('main_image')
            if main_image:
                ProductImage.objects.create(
                    product=product,
                    image=main_image,
                    is_main=True
                )

            selected_sizes = request.POST.getlist('sizes')
            for size_id in selected_sizes:
                try:
                    size = Size.objects.get(id=size_id)
                    stock = request.POST.get(f'stock_{size_id}', 10)
                    ProductSize.objects.create(
                        product=product,
                        size=size,
                        stock=int(stock) if stock else 10
                    )
                except Size.DoesNotExist:
                    pass

            additional_images = request.FILES.getlist('additional_images')
            for img in additional_images:
                ProductImage.objects.create(
                    product=product,
                    image=img,
                    is_main=False
                )

            messages.success(request, f'Товар "{product.name}" успішно створено!')

            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'seller/product_created.html', {'product': product})
            return redirect('seller:product_list')

        categories = Category.objects.all()
        sizes = Size.objects.all()

        context = {
            'form': form,
            'categories': categories,
            'sizes': sizes,
            'errors': form.errors,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'seller/product_form_content.html', context)
        return render(request, 'seller/product_form.html', context)


class SellerProductUpdateView(LoginRequiredMixin, SellerRequiredMixin, View):

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, seller=request.user)
        form = ProductForm(instance=product)
        categories = Category.objects.all()
        sizes = Size.objects.all()
        product_sizes = product.product_sizes.values_list('size_id', flat=True)

        context = {
            'form': form,
            'product': product,
            'categories': categories,
            'sizes': sizes,
            'product_sizes': list(product_sizes),
            'is_edit': True,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'seller/product_form_content.html', context)
        return render(request, 'seller/product_form.html', context)

    @transaction.atomic
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, seller=request.user)
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            product = form.save()

            main_image = request.FILES.get('main_image')
            if main_image:
                ProductImage.objects.filter(product=product, is_main=True).delete()
                ProductImage.objects.create(
                    product=product,
                    image=main_image,
                    is_main=True
                )

            selected_sizes = request.POST.getlist('sizes')

            product.product_sizes.exclude(size_id__in=selected_sizes).delete()

            for size_id in selected_sizes:
                try:
                    size = Size.objects.get(id=size_id)
                    stock = request.POST.get(f'stock_{size_id}', 10)
                    ProductSize.objects.update_or_create(
                        product=product,
                        size=size,
                        defaults={'stock': int(stock) if stock else 10}
                    )
                except Size.DoesNotExist:
                    pass

            additional_images = request.FILES.getlist('additional_images')
            for img in additional_images:
                ProductImage.objects.create(
                    product=product,
                    image=img,
                    is_main=False
                )

            messages.success(request, f'Товар "{product.name}" успішно оновлено!')

            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'seller/product_updated.html', {'product': product})
            return redirect('seller:product_list')

        categories = Category.objects.all()
        sizes = Size.objects.all()

        context = {
            'form': form,
            'product': product,
            'categories': categories,
            'sizes': sizes,
            'errors': form.errors,
            'is_edit': True,
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'seller/product_form_content.html', context)
        return render(request, 'seller/product_form.html', context)


class SellerProductDeleteView(LoginRequiredMixin, SellerRequiredMixin, View):

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, seller=request.user)
        product_name = product.name
        product.delete()

        messages.success(request, f'Товар "{product_name}" видалено!')

        if request.headers.get('HX-Request'):
            products = Product.objects.filter(seller=request.user).order_by('-created_at')
            return TemplateResponse(request, 'seller/product_list_content.html', {'products': products})
        return redirect('seller:product_list')


class SellerProductImageDeleteView(LoginRequiredMixin, SellerRequiredMixin, View):

    def post(self, request, image_id):
        image = get_object_or_404(ProductImage, id=image_id, product__seller=request.user)
        product = image.product
        image.delete()

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'seller/partials/product_images.html', {'product': product})
        return redirect('seller:product_edit', slug=product.slug)


class SellerDashboardView(LoginRequiredMixin, SellerRequiredMixin, View):

    def get(self, request):
        products = Product.objects.filter(seller=request.user)

        context = {
            'total_products': products.count(),
            'active_products': products.filter(is_available=True).count(),
            'recent_products': products.order_by('-created_at')[:5],
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'seller/dashboard_content.html', context)
        return render(request, 'seller/dashboard.html', context)