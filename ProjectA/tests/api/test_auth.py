import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestRegistration:

    def test_register_success(self, api_client):
        data = {
            'email': 'newuser@example.com',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert 'user' in response.data
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_register_password_mismatch(self, api_client):
        data = {
            'email': 'newuser@example.com',
            'password': 'strongpass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_existing_email(self, api_client, user):
        data = {
            'email': user.email,
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, api_client):
        data = {
            'email': 'invalid-email',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:

    def test_login_success(self, api_client, user):
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data

    def test_login_wrong_password(self, api_client, user):
        data = {
            'email': user.email,
            'password': 'wrongpassword'
        }
        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields(self, api_client):
        response = api_client.post('/api/auth/login/', {'password': 'test'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestLogout:

    def test_logout_success(self, auth_client, user):
        response = auth_client.post('/api/auth/logout/')

        assert response.status_code == status.HTTP_200_OK
        assert not Token.objects.filter(user=user).exists()

    def test_logout_unauthorized(self, api_client):
        response = api_client.post('/api/auth/logout/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCurrentUser:

    def test_get_current_user(self, auth_client, user):
        response = auth_client.get('/api/auth/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name

    def test_get_current_user_unauthorized(self, api_client):
        response = api_client.get('/api/auth/me/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_current_user(self, auth_client, user):
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = auth_client.patch('/api/auth/me/', data, format='json')

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'