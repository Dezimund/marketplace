import pytest
from decimal import Decimal
from django.db import IntegrityError

from main.models import Category, Product, Size, ProductSize
from cart.models import Cart, CartItem
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:

    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_user_str(self, user):
        assert str(user) == user.email

    def test_user_full_name(self, user):
        assert user.get_full_name() == f'{user.first_name} {user.last_name}'

    def test_email_unique(self, user):
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email=user.email,
                password='anotherpass',
                first_name='Another',
                last_name='User'
            )

@pytest.mark.django_db
class TestCategoryModel:

    def test_create_category(self):
        category = Category.objects.create(
            name='Електроніка',
            slug='elektronika'
        )

        assert category.name == 'Електроніка'
        assert category.slug == 'elektronika'
        assert not category.requires_size

    def test_category_str(self, category):
        assert str(category) == category.name

    def test_category_slug_unique(self, category):
        with pytest.raises(IntegrityError):
            Category.objects.create(
                name='Other',
                slug=category.slug
            )

    def test_category_products_count(self, category, products):
        assert category.products.count() == 5

@pytest.mark.django_db
class TestProductModel:

    def test_create_product(self, category, seller):
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=category,
            price=Decimal('999.99'),
            seller=seller
        )

        assert product.name == 'Test Product'
        assert product.price == Decimal('999.99')

    def test_product_str(self, product):
        assert str(product) == product.name

    def test_product_discount_percent(self, product_with_discount):
        expected = round((1 - 39999/44999) * 100)
        assert product_with_discount.discount_percent == expected

    def test_product_no_discount(self, product):
        assert product.discount_percent == 0

    def test_product_slug_unique(self, product, category, seller):
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name='Another Product',
                slug=product.slug,
                category=category,
                price=Decimal('100.00'),
                seller=seller
            )



@pytest.mark.django_db
class TestProductSizeModel:

    def test_create_product_size(self, product_with_sizes):
        assert product_with_sizes.product_sizes.count() == 4

    def test_product_size_stock(self, product_with_sizes):
        ps = product_with_sizes.product_sizes.first()
        assert ps.stock == 10

    def test_product_size_str(self, product_with_sizes):
        ps = product_with_sizes.product_sizes.first()
        assert ps.size.name in str(ps)
        assert product_with_sizes.name in str(ps)


@pytest.mark.django_db
class TestCartModel:

    def test_create_cart(self):
        cart = Cart.objects.create(session_key='test-session')

        assert cart.session_key == 'test-session'
        assert cart.total_items == 0
        assert cart.subtotal == 0

    def test_cart_str(self, cart):
         assert cart.session_key in str(cart)

    def test_cart_total_items(self, cart_with_items):
         assert cart_with_items.total_items == 3

    def test_cart_subtotal(self, cart_with_items):
        expected = Decimal('49999.00') * 2 + Decimal('39999.00')
        assert cart_with_items.subtotal == expected



@pytest.mark.django_db
class TestCartItemModel:

    def test_create_cart_item(self, cart, product):
        item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )

        assert item.quantity == 2
        assert item.product == product

    def test_cart_item_total_price(self, cart, product):
        item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=3
        )

        expected = product.price * 3
        assert item.total_price == expected

    def test_cart_item_with_size(self, cart, product_with_sizes):
        ps = product_with_sizes.product_sizes.first()

        item = CartItem.objects.create(
            cart=cart,
            product=product_with_sizes,
            product_size=ps,
            quantity=1
        )

        assert item.product_size == ps