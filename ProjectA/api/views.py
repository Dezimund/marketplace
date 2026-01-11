from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend
from main.models import Category, Product, ProductSize, Size
from cart.models import Cart, CartItem
from users.models import CustomUser
from orders.models import Order, OrderItem
from decimal import Decimal
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, SizeSerializer, ProductSizeSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UserSerializer, UserDetailSerializer, UserRegistrationSerializer
)
from .permissions import IsOwnerOrReadOnly, IsSellerOrReadOnly


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Реєстрація успішна'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email та пароль обов\'язкові'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        return Response(
            {'error': 'Невірний email або пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Вихід успішний'})
        except Exception:
            return Response({'message': 'Вихід успішний'})


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserDetailSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        user = self.get_object()
        if not user.is_seller:
            return Response(
                {'error': 'Користувач не є продавцем'},
                status=status.HTTP_404_NOT_FOUND
            )
        products = Product.objects.filter(seller=user)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)

        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        color = request.query_params.get('color')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if color:
            products = products.filter(color__iexact=color)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'color', 'is_new', 'is_bestseller', 'is_recommended']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'views_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return ProductDetailSerializer

    def create(self, request, *args, **kwargs):
        print("=== CREATE PRODUCT ===")
        print("Data:", dict(request.data))
        print("User:", request.user)
        print("Is authenticated:", request.user.is_authenticated)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = Product.objects.all()

        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        has_discount = self.request.query_params.get('has_discount')
        color = self.request.query_params.get('color')
        size = self.request.query_params.get('size')
        in_stock = self.request.query_params.get('in_stock')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if has_discount:
            queryset = queryset.filter(old_price__isnull=False, old_price__gt=F('price'))
        if color:
            queryset = queryset.filter(color__icontains=color)

        if size:
            if size.isdigit():
                queryset = queryset.filter(product_sizes__size_id=size, product_sizes__stock__gt=0)
            else:
                queryset = queryset.filter(product_sizes__size__name__iexact=size, product_sizes__stock__gt=0)
            queryset = queryset.distinct()

        if in_stock == 'true':
            from django.db.models import Sum, IntegerField
            from django.db.models.functions import Coalesce

            queryset = queryset.annotate(
                sizes_stock=Coalesce(Sum('product_sizes__stock'), 0, output_field=IntegerField())
            )

            queryset = queryset.filter(
                Q(category__requires_size=True, sizes_stock__gt=0) |
                Q(category__requires_size=False, stock__gt=0) |
                Q(category__isnull=True, stock__gt=0)
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Product.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        products = Product.objects.filter(is_recommended=True)[:12]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        products = Product.objects.filter(is_bestseller=True)[:12]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new(self, request):
        products = Product.objects.filter(is_new=True)[:12]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        products = Product.objects.order_by('-views_count')[:12]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sale(self, request):
        products = Product.objects.filter(
            old_price__isnull=False,
            old_price__gt=F('price')
        )[:12]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        product = self.get_object()
        related = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:8]
        serializer = ProductListSerializer(related, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_size(self, request, slug=None):
        product = self.get_object()

        if product.seller != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Немає прав для редагування'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSizeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_cart(self, request):
        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart = self.get_cart(request)
        serializer = AddToCartSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product = Product.objects.get(id=data['product_id'])
        product_size = None

        if data.get('product_size_id'):
            product_size = ProductSize.objects.get(id=data['product_size_id'])
        elif product.category.requires_size:
            product_size = product.product_sizes.filter(stock__gt=0).first()
            if not product_size:
                return Response(
                    {'error': 'Немає доступних розмірів'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if product_size and product_size.stock < data['quantity']:
            return Response(
                {'error': f'Доступно лише {product_size.stock} шт.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            product_size=product_size,
            defaults={'quantity': data['quantity']}
        )

        if not created:
            new_quantity = cart_item.quantity + data['quantity']
            if product_size and new_quantity > product_size.stock:
                return Response(
                    {'error': f'Максимальна кількість: {product_size.stock} шт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()

        return Response({
            'message': 'Товар додано до кошика',
            'cart': CartSerializer(cart).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='update/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        cart = self.get_cart(request)

        try:
            cart_item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Товар не знайдено в кошику'},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity', 1)

        if quantity <= 0:
            cart_item.delete()
            return Response({
                'message': 'Товар видалено з кошика',
                'cart': CartSerializer(cart).data
            })

        if cart_item.product_size and quantity > cart_item.product_size.stock:
            return Response(
                {'error': f'Доступно лише {cart_item.product_size.stock} шт.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response({
            'message': 'Кількість оновлено',
            'cart': CartSerializer(cart).data
        })

    @action(detail=False, methods=['delete'], url_path='remove/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        cart = self.get_cart(request)

        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass

        return Response({
            'message': 'Товар видалено',
            'cart': CartSerializer(cart).data
        })

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()

        return Response({
            'message': 'Кошик очищено',
            'cart': CartSerializer(cart).data
        })

    @action(detail=False, methods=['get'])
    def count(self, request):
        cart = self.get_cart(request)
        return Response({
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal)
        })


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        data = []
        for order in orders:
            data.append({
                'id': order.id,
                'status': order.status,
                'total_price': str(order.total_price),
                'created_at': order.created_at.isoformat(),
                'city': order.city,
                'address1': order.address1,
                'items_count': order.items.count(),
            })
        return Response(data)

    def retrieve(self, request, pk=None):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Замовлення не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )

        items_data = []
        for item in order.items.select_related('product', 'size__size'):
            items_data.append({
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'slug': item.product.slug,
                    'main_image': item.product.main_image.url if item.product.main_image else None,
                },
                'size': {
                    'id': item.size.id if item.size else None,
                    'size': {'name': item.size.size.name} if item.size else None,
                } if item.size else None,
                'quantity': item.quantity,
                'price': str(item.price),
            })

        data = {
            'id': order.id,
            'status': order.status,
            'payment_provider': order.payment_provider,
            'first_name': order.first_name,
            'last_name': order.last_name,
            'email': order.email,
            'phone_number': order.phone_number,
            'country': order.country,
            'city': order.city,
            'address1': order.address1,
            'address2': order.address2,
            'postal_code': order.postal_code,
            'total_price': str(order.total_price),
            'created_at': order.created_at.isoformat(),
            'items': items_data,
        }
        return Response(data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        if not request.session.session_key:
            return Response(
                {'error': 'Кошик порожній'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Кошик порожній'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cart.total_items == 0:
            return Response(
                {'error': 'Кошик порожній'},
                status=status.HTTP_400_BAD_REQUEST
            )

        required_fields = ['first_name', 'last_name']
        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {'error': f'Поле {field} обов\'язкове'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            user=request.user,
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            email=request.data.get('email', request.user.email),
            company=request.data.get('company', ''),
            address1=request.data.get('address1', ''),
            address2=request.data.get('address2', ''),
            city=request.data.get('city', ''),
            country=request.data.get('country', ''),
            state=request.data.get('state', ''),
            postal_code=request.data.get('postal_code', ''),
            phone_number=request.data.get('phone_number', ''),
            total_price=cart.subtotal,
            payment_provider=request.data.get('payment_provider'),
        )

        for item in cart.items.select_related('product', 'product_size'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                size=item.product_size,
                quantity=item.quantity,
                price=item.product.price or Decimal('0.00'),
            )

            if item.product_size:
                item.product_size.stock = max(0, item.product_size.stock - item.quantity)
                item.product_size.save(update_fields=['stock'])
            elif hasattr(item.product, 'stock') and item.product.stock is not None:
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save(update_fields=['stock'])

        cart.items.all().delete()

        return Response({
            'message': 'Замовлення створено',
            'order_id': order.id,
        }, status=status.HTTP_201_CREATED)