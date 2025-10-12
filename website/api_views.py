"""
Django REST Framework ViewSets
API endpoints for mobile app
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import Shipment, Bid, UserProfile, Vehicle
from .serializers import (
    ShipmentSerializer, ShipmentListSerializer, ShipmentCreateSerializer,
    BidSerializer, BidCreateSerializer,
    UserProfileSerializer, VehicleSerializer
)


class ShipmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Shipment model

    list: Get all active shipments
    retrieve: Get single shipment by ID
    create: Create new shipment (authenticated users only)
    update: Update shipment (owner only)
    destroy: Delete shipment (owner only)
    """
    queryset = Shipment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'cargo_type', 'from_address_city', 'to_address_city']
    search_fields = ['title', 'description', 'tracking_number']
    ordering_fields = ['created_at', 'suggested_price', 'pickup_date', 'view_count', 'bid_count']
    ordering = ['-created_at']
    lookup_field = 'shipment_id'

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ShipmentListSerializer
        elif self.action == 'create':
            return ShipmentCreateSerializer
        return ShipmentSerializer

    def get_queryset(self):
        """Filter queryset based on user and query params"""
        queryset = Shipment.objects.all()

        # Filter by status (default: show only active)
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        elif self.action == 'list':
            # By default, only show active shipments in list view
            queryset = queryset.filter(status='active')

        return queryset.select_related('shipper__user').prefetch_related('bids')

    def retrieve(self, request, *args, **kwargs):
        """Get shipment detail and increment view count"""
        instance = self.get_object()

        # Increment view count (only if not the owner)
        if not request.user.is_authenticated or (
            hasattr(request.user, 'profile') and
            request.user.profile != instance.shipper
        ):
            instance.increment_view_count()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_shipments(self, request):
        """Get current user's shipments"""
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        shipments = Shipment.objects.filter(shipper=profile).order_by('-created_at')

        serializer = ShipmentListSerializer(shipments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assign_carrier(self, request, shipment_id=None):
        """Assign a carrier to shipment (accept bid)"""
        shipment = self.get_object()

        # Check if user is the owner
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        if shipment.shipper != profile:
            return Response(
                {'error': 'You do not have permission to assign carrier'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get bid_id from request
        bid_id = request.data.get('bid_id')
        shipper_comment = request.data.get('shipper_comment', '')

        if not bid_id:
            return Response(
                {'error': 'bid_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get bid
        try:
            bid = Bid.objects.get(bid_id=bid_id, shipment=shipment)
        except Bid.DoesNotExist:
            return Response(
                {'error': 'Bid not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update bid
        bid.status = 'accepted'
        bid.accepted_at = timezone.now()
        if shipper_comment:
            bid.shipper_comment = shipper_comment
        bid.save()

        # Update shipment
        shipment.status = 'assigned'
        shipment.assigned_carrier_uid = bid.carrier_uid
        shipment.assigned_bid_id = bid_id
        shipment.final_price = bid.offered_price
        shipment.save()

        # Reject other pending bids
        Bid.objects.filter(shipment=shipment, status='pending').exclude(bid_id=bid_id).update(
            status='rejected',
            updated_at=timezone.now()
        )

        serializer = self.get_serializer(shipment)
        return Response(serializer.data)


class BidViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bid model

    list: Get all bids (filtered by shipment or carrier)
    retrieve: Get single bid
    create: Submit new bid (carriers only)
    update: Update bid (partial updates allowed)
    destroy: Delete/withdraw bid (owner only)
    """
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'shipment', 'carrier_uid']
    ordering_fields = ['created_at', 'offered_price']
    ordering = ['-created_at']
    lookup_field = 'bid_id'

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return BidCreateSerializer
        return BidSerializer

    def get_queryset(self):
        """Filter queryset based on user"""
        queryset = Bid.objects.all()

        # Filter by shipment
        shipment_id = self.request.query_params.get('shipment_id', None)
        if shipment_id:
            queryset = queryset.filter(shipment__shipment_id=shipment_id)

        # Filter by tracking number
        tracking_number = self.request.query_params.get('tracking_number', None)
        if tracking_number:
            queryset = queryset.filter(tracking_number=tracking_number)

        return queryset.select_related('shipment')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_bids(self, request):
        """Get current user's bids"""
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        bids = Bid.objects.filter(carrier=profile).order_by('-created_at')

        serializer = self.get_serializer(bids, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def withdraw(self, request, bid_id=None):
        """Withdraw a bid"""
        bid = self.get_object()

        # Check if user is the owner
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        if bid.carrier != profile:
            return Response(
                {'error': 'You do not have permission to withdraw this bid'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Only pending bids can be withdrawn
        if bid.status != 'pending':
            return Response(
                {'error': f'Cannot withdraw bid with status: {bid.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bid.status = 'withdrawn'
        bid.save()

        # Update shipment bid count
        shipment = bid.shipment
        shipment.bid_count = shipment.bids.exclude(status='withdrawn').count()
        shipment.save(update_fields=['bid_count'])

        serializer = self.get_serializer(bid)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for UserProfile model (read-only for now)

    list: Get all verified carriers
    retrieve: Get single user profile
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_type', 'documents_verified']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company_name']

    def get_queryset(self):
        """Filter to show only carriers with verified documents"""
        queryset = UserProfile.objects.filter(user_type=1, documents_verified=True)
        return queryset.select_related('user')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's profile"""
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle model

    list: Get all vehicles (filtered by carrier)
    retrieve: Get single vehicle
    create: Add new vehicle (carriers only)
    update: Update vehicle (owner only)
    destroy: Delete vehicle (owner only)
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['vehicle_type', 'is_active', 'carrier_profile']
    ordering_fields = ['created_at', 'year']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter vehicles by carrier"""
        queryset = Vehicle.objects.filter(is_active=True)

        # Filter by carrier profile ID
        carrier_id = self.request.query_params.get('carrier_id', None)
        if carrier_id:
            queryset = queryset.filter(carrier_profile_id=carrier_id)

        return queryset.select_related('carrier_profile__user')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_vehicles(self, request):
        """Get current user's vehicles"""
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        vehicles = Vehicle.objects.filter(carrier_profile=profile).order_by('-created_at')

        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)
