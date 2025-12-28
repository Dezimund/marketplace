from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.template.response import TemplateResponse
from .models import Category, Product, Size
from django.db.models import Q, F


class IndexView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None

        context['recommended_products'] = Product.objects.filter(
            is_recommended=True
        ).order_by('-created_at')[:8]

        context['bestseller_products'] = Product.objects.filter(
            is_bestseller=True
        ).order_by('-created_at')[:8]

        context['new_products'] = Product.objects.filter(
            is_new=True
        ).order_by('-created_at')[:8]

        context['popular_products'] = Product.objects.all().order_by(
            '-views_count'
        )[:8]

        context['sale_products'] = Product.objects.filter(
            old_price__isnull=False,
            old_price__gt=F('price')
        ).order_by('-created_at')[:8]

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/home_content.html', context)
        return TemplateResponse(request, self.template_name, context)


class CatalogView(TemplateView):
    template_name = 'main/base.html'

    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color__iexact=value),
        'min_price': lambda queryset, value: queryset.filter(price__gte=value),
        'max_price': lambda queryset, value: queryset.filter(price__lte=value),
        'size': lambda queryset, value: queryset.filter(product_sizes__size__name=value)
    }

    SORT_MAPPING = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'popular': '-views_count',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug')
        categories = Category.objects.all()
        products = Product.objects.all()
        current_category = None

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)

        query = self.request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = ''

        filter_params['q'] = query or ''

        sort = self.request.GET.get('sort', 'newest')
        order_by = self.SORT_MAPPING.get(sort, '-created_at')
        products = products.order_by(order_by)

        products = products.distinct()

        context.update({
            'categories': categories,
            'products': products,
            'current_category': category_slug,
            'filter_params': filter_params,
            'sizes': Size.objects.all(),
            'search_query': query or '',
            'current_sort': sort,
        })

        if self.request.GET.get('show_search') == 'true':
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            context['reset_search'] = True

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get('HX-Request'):
            if context.get('show_search'):
                return TemplateResponse(request, 'main/search_input.html', context)
            elif context.get('reset_search'):
                return TemplateResponse(request, 'main/search_button.html', {})
            elif request.GET.get('show_filters') == 'true':
                return TemplateResponse(request, 'main/filter_modal.html', context)
            return TemplateResponse(request, 'main/catalog.html', context)

        return TemplateResponse(request, self.template_name, context)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/base.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related(
            'images', 'product_sizes__size'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['categories'] = Category.objects.all()
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).select_related('category')[:4]
        context['current_category'] = product.category.slug

        seller_name = None
        if product.seller_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                seller = User.objects.filter(pk=product.seller_id).first()
                if seller:
                    seller_name = getattr(seller, 'get_full_name', lambda: None)()
                    if not seller_name:
                        seller_name = getattr(seller, 'username', 'Магазин')
            except Exception:
                seller_name = None
        context['seller_name'] = seller_name

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        Product.objects.filter(pk=self.object.pk).update(
            views_count=F('views_count') + 1
        )

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/product_detail.html', context)

        return TemplateResponse(request, self.template_name, context)