from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Vehicle
from .serializers import VehicleSerializer, VehicleCreateSerializer

class VehicleListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehicle_type', 'is_available', 'year']
    search_fields = ['make', 'model', 'plate_number']
    ordering_fields = ['created_at', 'year', 'daily_rate']
    ordering = ['-created_at']

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VehicleCreateSerializer
        return VehicleSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         vehicle = serializer.save()
    #         return Response({
    #             'message': 'Vehicle added successfully',
    #             'vehicle': VehicleSerializer(vehicle).data
    #         }, status=status.HTTP_201_CREATED)
    #     return Response({
    #         'error': 'Vehicle creation failed',
    #         'details': serializer.errors
    #     }, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)  # This will set the owner
            return Response({
                'message': 'Vehicle added successfully',
                'vehicle': VehicleSerializer(serializer.instance).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error': 'Vehicle creation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VehicleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VehicleSerializer

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            vehicle = serializer.save()
            return Response({
                'message': 'Vehicle updated successfully',
                'vehicle': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'Vehicle update failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if vehicle has active bookings
        # if instance.bookings.filter(status='confirmed').exists():
        #     return Response({
        #         'error': 'Cannot delete vehicle with active bookings'
        #     }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(instance)
        return Response({
            'message': 'Vehicle deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
