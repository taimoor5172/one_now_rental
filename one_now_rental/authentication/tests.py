from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testrenter',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Renter',
            'phone': '+923491234567',
            'user_type': 'renter',
        }
    
    def test_user_registration_success(self):

        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
    
    def test_user_registration_duplicate_email(self):
       
        User.objects.create_user(username='existing', email='test@example.com', password='pass123')
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_password_mismatch(self):
        
        data = self.user_data.copy()
        data['password_confirm'] = 'differentpass'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        
        user = User.objects.create_user(
            username='testrenter',
            email='test@example.com',
            password='testpass123'
        )
        login_data = {
            'username': 'testrenter',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        User.objects.create_user(
            username='testrenter',
            email='test@example.com',
            password='testpass123'
        )
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_weak_password(self):
        """Test registration with weak password"""
        data = self.user_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)