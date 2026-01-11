import pytest
from decimal import Decimal
from rest_framework import status

from main.models import Category, Product


@pytest.mark.django_db
class TestCategoryAPI:

    def test_list_categories(self, api_client, categories):
        response = api_client.get('/api/categories/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_retrieve_category(self, api_client, category):
        response = api_client.get(f'/api/categories/{category.slug}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name
        assert response.data['slug'] == category.slug

    def test_category_products(self, api_client, category, products):
        response = api_client.get(f'/api/categories/{category.slug}/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_create_category_unauthorized(self, api_client):
        data = {'name': 'New Category', 'slug': 'new-category'}
        response = api_client.post('/api/categories/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProductAPI:
    def test_list_products(self, api_client, products):

        response = api_client.get('/api/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_retrieve_product(self, api_client, product):
        response = api_client.get(f'/api/products/{product.slug}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name
        assert response.data['slug'] == product.slug

    def test_product_views_count_increment(self, api_client, product):
        initial_views = product.views_count

        api_client.get(f'/api/products/{product.slug}/')
        product.refresh_from_db()

        assert product.views_count == initial_views + 1

    def test_filter_by_category_slug(self, api_client, category, products):
        response = api_client.get('/api/products/', {'category_slug': category.slug})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_filter_by_price_range(self, api_client, products):
        response = api_client.get('/api/products/', {'min_price': 2000, 'max_price': 4000})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_search_products(self, api_client, product):
        response = api_client.get('/api/products/', {'search': 'iPhone'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_ordering_by_price(self, api_client, products):
        response = api_client.get('/api/products/', {'ordering': 'price'})

        assert response.status_code == status.HTTP_200_OK
        prices = [Decimal(p['price']) for p in response.data]
        assert prices == sorted(prices)

    def test_ordering_by_price_desc(self, api_client, products):
        response = api_client.get('/api/products/', {'ordering': '-price'})

        assert response.status_code == status.HTTP_200_OK
        prices = [Decimal(p['price']) for p in response.data]
        assert prices == sorted(prices, reverse=True)

@pytest.mark.django_db
class TestProductSpecialEndpoints:

    def test_recommended_products(self, api_client, db, category, seller):
        Product.objects.create(
            name='Recommended Product',
            slug='recommended-product',
            category=category,
            price=Decimal('1000.00'),
            seller=seller,
            is_recommended=True
        )

        response = api_client.get('/api/products/recommended/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_bestsellers(self, api_client, product_with_discount):
        response = api_client.get('/api/products/bestsellers/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_new_products(self, api_client, product):
        response = api_client.get('/api/products/new/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_sale_products(self, api_client, product_with_discount):
        response = api_client.get('/api/products/sale/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_related_products(self, api_client, product, products):
        response = api_client.get(f'/api/products/{product.slug}/related/')

        assert response.status_code == status.HTTP_200_OK
        slugs = [p['slug'] for p in response.data]
        assert product.slug not in slugs


@pytest.mark.django_db
class TestProductDiscount:

    def test_discount_percent_calculation(self, product_with_discount):
        expected_discount = round(
            (1 - product_with_discount.price / product_with_discount.old_price) * 100
        )
        assert product_with_discount.discount_percent == expected_discount

    def test_no_discount_when_no_old_price(self, product):
        assert product.discount_percent == 0