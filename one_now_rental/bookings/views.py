from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer

class BookingFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    vehicle_make = filters.CharFilter(field_name='vehicle__make', lookup_expr='icontains')
    vehicle_model = filters.CharFilter(field_name='vehicle__model', lookup_expr='icontains')
    
    class Meta:
        model = Booking
        fields = ['status', 'from_date', 'to_date', 'vehicle_make', 'vehicle_model']

class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BookingFilter
    ordering_fields = ['created_at', 'start_date', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Booking.objects.filter(renter=self.request.user).select_related('vehicle')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        serializer.save(renter=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Booking created successfully',
                'booking': BookingSerializer(serializer.instance).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error': 'Booking creation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class BookingRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(renter=self.request.user).select_related('vehicle')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Only allow status updates for existing bookings
        allowed_fields = ['status', 'notes']
        filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = self.get_serializer(instance, data=filtered_data, partial=partial)
        if serializer.is_valid():
            booking = serializer.save()
            return Response({
                'message': 'Booking updated successfully',
                'booking': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'Booking update failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)