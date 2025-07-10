from rest_framework import serializers
from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'owner', 'make', 'model', 'year', 'plate_number', 
                 'vehicle_type', 'color', 'daily_rate', 'is_available', 
                 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate_plate_number(self, value):
        # Check if plate number already exists for other vehicles
        if self.instance:
            # Update case - exclude current instance
            if Vehicle.objects.filter(plate_number=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('Vehicle with this plate number already exists.')
        else:
            # Create case
            if Vehicle.objects.filter(plate_number=value).exists():
                raise serializers.ValidationError('Vehicle with this plate number already exists.')
        return value.upper()

    def validate_daily_rate(self, value):
        if value < 0:
            raise serializers.ValidationError('Daily rate cannot be negative.')
        return value

class VehicleCreateSerializer(VehicleSerializer):
    class Meta(VehicleSerializer.Meta):
        fields = ['make', 'model', 'year', 'plate_number', 'vehicle_type', 
                 'color', 'daily_rate', 'description']