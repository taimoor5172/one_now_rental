from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from vehicles.models import Vehicle
from .models import Booking

User = get_user_model()

class BookingTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vehicle_owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        
        # Authenticate the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create a vehicle owned by another user
        self.vehicle = Vehicle.objects.create(
            owner=self.vehicle_owner,
            make='Toyota',
            model='Camry',
            year=2020,
            plate_number='ABC123',
            daily_rate=75.00,
            is_available=True
        )
        
        self.booking_data = {
            'vehicle': self.vehicle.id,
            'start_date': "2025-07-10",
            'end_date': "2025-07-13",
            'notes': 'Weekend trip'
        }
        
        self.bookings_url = reverse('booking-list-create')
    
    def test_create_booking_success(self):
        """Test successful booking creation"""
        response = self.client.post(self.bookings_url, self.booking_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        booking = Booking.objects.get(pk=response.data['booking']['id'])
        self.assertEqual(booking.renter, self.user)
        self.assertEqual(booking.vehicle, self.vehicle)
        self.assertEqual(booking.total_amount, 225.00)  # 3 days * 75.00
    
    def test_create_booking_own_vehicle(self):
        """Test booking own vehicle (should fail)"""
        own_vehicle = Vehicle.objects.create(
            owner=self.user,
            make='Honda',
            model='Civic',
            year=2019,
            plate_number='OWN123',
            daily_rate=60.00
        )
        
        booking_data = self.booking_data.copy()
        booking_data['vehicle'] = own_vehicle.id
        
        response = self.client.post(self.bookings_url, booking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_booking_invalid_dates(self):
        """Test booking with invalid date range"""
        booking_data = self.booking_data.copy()
        booking_data['start_date'] = date.today() + timedelta(days=3)
        booking_data['end_date'] = date.today() + timedelta(days=1)
        
        response = self.client.post(self.bookings_url, booking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_booking_past_date(self):
        """Test booking with past start date"""
        booking_data = self.booking_data.copy()
        booking_data['start_date'] = date.today() - timedelta(days=1)
        booking_data['end_date'] = date.today() + timedelta(days=1)
        
        response = self.client.post(self.bookings_url, booking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_booking_conflicting_dates(self):
        """Test booking with conflicting dates"""
        # Create existing booking
        Booking.objects.create(
            renter=self.user,
            vehicle=self.vehicle,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=2),
        )
        
        # Try to book overlapping dates
        response = self.client.post(self.bookings_url, self.booking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    