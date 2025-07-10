from rest_framework import serializers
from django.db.models import Q
from .models import Booking
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from datetime import date, datetime

class BookingSerializer(serializers.ModelSerializer):
    renter = serializers.StringRelatedField(read_only=True)
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    days = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'renter', 'vehicle', 'vehicle_details', 'start_date', 
                 'end_date', 'days', 'total_amount', 'status', 'notes', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'renter', 'total_amount', 'created_at', 'updated_at']

    def get_days(self, obj):
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return 0

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['vehicle', 'start_date', 'end_date', 'notes']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        vehicle = attrs.get('vehicle')

        # Basic date validation
        if start_date >= end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })

        if start_date < date.today():
            raise serializers.ValidationError({
                'start_date': 'Start date cannot be in the past.'
            })

        # Check if vehicle exists and is available
        if not vehicle.is_available:
            raise serializers.ValidationError({
                'vehicle': 'Vehicle is not available for booking.'
            })

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            vehicle=vehicle,
            status__in=['pending', 'confirmed'],
        ).filter(
            Q(start_date__lte=start_date, end_date__gt=start_date) |
            Q(start_date__lt=end_date, end_date__gte=end_date) |
            Q(start_date__gte=start_date, end_date__lte=end_date)
        )

        if overlapping_bookings.exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Vehicle is already booked for the selected dates.'
            })

        return attrs

    def validate_vehicle(self, value):
        # Ensure user cannot book their own vehicle
        if value.owner == self.context['request'].user:
            raise serializers.ValidationError('You cannot book your own vehicle.')
        return value