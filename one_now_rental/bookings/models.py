from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from vehicles.models import Vehicle
from datetime import datetime, date
from decimal import Decimal

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['renter', 'status']),
            models.Index(fields=['vehicle', 'start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.renter.username} - {self.vehicle} ({self.start_date} to {self.end_date})"

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError('End date must be after start date.')
            
            if self.start_date < date.today():
                raise ValidationError('Start date cannot be in the past.')

    def save(self, *args, **kwargs):
        self.clean()
        
        if self.start_date and self.end_date and self.vehicle:
            # Calculate total amount
            days = (self.end_date - self.start_date).days
            self.total_amount = Decimal(str(days)) * Decimal(self.vehicle.daily_rate)
        
        super().save(*args, **kwargs)