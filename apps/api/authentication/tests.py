from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_sign_up(self):
        """Test user registration"""
        url = '/api/v1/auth/sign-up/'
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'testpass123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        self.assertIn('user', response.data)

    def test_sign_in(self):
        """Test user login"""
        # Create user
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        url = '/api/v1/auth/sign-in/'
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_sign_in_invalid_credentials(self):
        """Test login with wrong password"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        url = '/api/v1/auth/sign-in/'
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sign_out(self):
        """Test user logout"""
        # Create and login user
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)

        url = '/api/v1/auth/sign-out/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile(self):
        """Test getting user profile"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=user)

        url = '/api/v1/auth/profile/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')

    def test_profile_unauthenticated(self):
        """Test profile endpoint requires authentication"""
        url = '/api/v1/auth/profile/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
