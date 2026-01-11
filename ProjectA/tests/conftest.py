import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from main.models import Category, Product, Size, ProductSize
from cart.models import Cart, CartItem


User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='user@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def seller(db):
    return User.objects.create_user(
        email='seller@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Seller',
        is_seller=True
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def auth_client(api_client, user):
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def seller_client(api_client, seller):
    token, _ = Token.objects.get_or_create(user=seller)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def category(db):

    return Category.objects.create(
        name='Смартфони',
        slug='smartfoni',
        requires_size=False
    )


@pytest.fixture
def category_with_sizes(db):
    return Category.objects.create(
        name='Одяг',
        slug='odyag',
        requires_size=True
    )


@pytest.fixture
def categories(db):
    return [
        Category.objects.create(name='Смартфони', slug='smartfoni', requires_size=False),
        Category.objects.create(name='Одяг', slug='odyag', requires_size=True),
        Category.objects.create(name='Взуття', slug='vzuttya', requires_size=True),
    ]


@pytest.fixture
def sizes(db):
    return [
        Size.objects.create(name='S'),
        Size.objects.create(name='M'),
        Size.objects.create(name='L'),
        Size.objects.create(name='XL'),
    ]


@pytest.fixture
def product(db, category, seller):
    return Product.objects.create(
        name='iPhone 15 Pro',
        slug='iphone-15-pro',
        category=category,
        price=Decimal('49999.00'),
        description='Найновіший iPhone',
        color='Black',
        seller=seller,
        is_new=True
    )


@pytest.fixture
def product_with_discount(db, category, seller):
    return Product.objects.create(
        name='Samsung Galaxy S24',
        slug='samsung-galaxy-s24',
        category=category,
        price=Decimal('39999.00'),
        old_price=Decimal('44999.00'),
        description='Флагман Samsung',
        color='White',
        seller=seller,
        is_bestseller=True
    )


@pytest.fixture
def product_with_sizes(db, category_with_sizes, seller, sizes):
    product = Product.objects.create(
        name='Футболка Nike',
        slug='futbolka-nike',
        category=category_with_sizes,
        price=Decimal('1299.00'),
        description='Спортивна футболка',
        color='Blue',
        seller=seller
    )

    for size in sizes:
        ProductSize.objects.create(
            product=product,
            size=size,
            stock=10
        )

    return product


@pytest.fixture
def products(db, category, seller):
    return [
        Product.objects.create(
            name=f'Product {i}',
            slug=f'product-{i}',
            category=category,
            price=Decimal(f'{1000 * i}.00'),
            seller=seller,
            is_new=(i % 2 == 0),
            is_bestseller=(i % 3 == 0),
        )
        for i in range(1, 6)
    ]


@pytest.fixture
def cart(db):
    return Cart.objects.create(session_key='test-session-key')


@pytest.fixture
def cart_with_items(db, cart, product, product_with_discount):
    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2
    )
    CartItem.objects.create(
        cart=cart,
        product=product_with_discount,
        quantity=1
    )
    return cart


@pytest.fixture
def cart_with_sized_item(db, cart, product_with_sizes):
    product_size = product_with_sizes.product_sizes.first()
    CartItem.objects.create(
        cart=cart,
        product=product_with_sizes,
        product_size=product_size,
        quantity=1
    )
    return cart