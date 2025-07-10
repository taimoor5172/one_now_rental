from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Vehicle

User = get_user_model()

class VehicleTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Authenticate the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.vehicle_data = {
            "make": "Toyota",
            "model": "Camry",
            "year": 2023,
            "plate_number": "ABC123",
            "vehicle_type": "sedan",
            "daily_rate": 45.00,
            'description': 'Well maintained sedan'
        }
        
        self.vehicles_url = reverse('vehicle-list-create')
    
    def test_create_vehicle_success(self):
        """Test successful vehicle creation"""
        response = self.client.post(self.vehicles_url, self.vehicle_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Vehicle.objects.filter(plate_number='ABC123').exists())
        vehicle = Vehicle.objects.get(plate_number='ABC123')
        self.assertEqual(vehicle.owner, self.user)
    
    def test_create_vehicle_duplicate_plate(self):
        """Test vehicle creation with duplicate plate number"""
        Vehicle.objects.create(owner=self.other_user, **self.vehicle_data)
        response = self.client.post(self.vehicles_url, self.vehicle_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_user_vehicles_only(self):
        """Test that users can only see their own vehicles"""
        # Create vehicles for both users
        Vehicle.objects.create(owner=self.user, **self.vehicle_data)
        other_vehicle_data = self.vehicle_data.copy()
        other_vehicle_data['plate_number'] = 'XYZ789'
        Vehicle.objects.create(owner=self.other_user, **other_vehicle_data)
        
        response = self.client.get(self.vehicles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['plate_number'], 'ABC123')
    
    def test_update_vehicle_success(self):
        """Test successful vehicle update"""
        vehicle = Vehicle.objects.create(owner=self.user, **self.vehicle_data)
        update_url = reverse('vehicle-detail', kwargs={'pk': vehicle.pk})
        update_data = {'daily_rate': 85.00}
        
        response = self.client.patch(update_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.daily_rate, 85.00)
    
    def test_delete_vehicle_success(self):
        """Test successful vehicle deletion"""
        vehicle = Vehicle.objects.create(owner=self.user, **self.vehicle_data)
        delete_url = reverse('vehicle-detail', kwargs={'pk': vehicle.pk})
        
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Vehicle.objects.filter(pk=vehicle.pk).exists())
    
    def test_access_other_user_vehicle(self):
        """Test that users cannot access other users' vehicles"""
        vehicle = Vehicle.objects.create(owner=self.other_user, **self.vehicle_data)
        detail_url = reverse('vehicle-detail', kwargs={'pk': vehicle.pk})
        
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    