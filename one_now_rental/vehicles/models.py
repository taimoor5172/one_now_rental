from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

User = get_user_model()

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('truck', 'Truck'),
        ('van', 'Van'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.now().year + 1)
        ]
    )
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=15, choices=VEHICLE_TYPES, default='sedan')
    color = models.CharField(max_length=30, blank=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_available']),
            models.Index(fields=['plate_number']),
        ]

    def __str__(self):
        return f"{self.year} {self.make} {self.model} - {self.plate_number}"