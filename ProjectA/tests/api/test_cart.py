import pytest
from decimal import Decimal
from rest_framework import status

from cart.models import Cart, CartItem


@pytest.mark.django_db
class TestCartAPI:

    def test_get_cart_creates_new(self, api_client):
        response = api_client.get('/api/cart/')

        assert response.status_code == status.HTTP_200_OK
        assert 'items' in response.data
        assert response.data['total_items'] == 0

    def test_cart_total_items(self, cart_with_items):
        assert cart_with_items.total_items == 3  # 2 + 1

    def test_cart_subtotal(self, cart_with_items):
        expected = Decimal('49999.00') * 2 + Decimal('39999.00') * 1
        assert cart_with_items.subtotal == expected

@pytest.mark.django_db
class TestAddToCart:

    def test_add_product_to_cart(self, api_client, product):
        data = {
            'product_id': product.id,
            'quantity': 1
        }
        response = api_client.post('/api/cart/add/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'cart' in response.data
        assert response.data['cart']['total_items'] == 1

    def test_add_product_with_quantity(self, api_client, product):
        data = {
            'product_id': product.id,
            'quantity': 3
        }
        response = api_client.post('/api/cart/add/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['cart']['total_items'] == 3

    def test_add_invalid_product(self, api_client):
        data = {
            'product_id': 99999,
            'quantity': 1
        }
        response = api_client.post('/api/cart/add/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_with_invalid_quantity(self, api_client, product):
        data = {
            'product_id': product.id,
            'quantity': 0
        }
        response = api_client.post('/api/cart/add/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestClearCart:

    def test_clear_cart(self, api_client, cart_with_items):
        session = api_client.session
        session.create()
        cart_with_items.session_key = session.session_key
        cart_with_items.save()

        response = api_client.delete('/api/cart/clear/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['cart']['total_items'] == 0

@pytest.mark.django_db
class TestCartCount:

    def test_cart_count_empty(self, api_client):
        response = api_client.get('/api/cart/count/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0