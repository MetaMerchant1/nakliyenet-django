"""
Django REST Framework Serializers
API için model serileştirme
"""
from rest_framework import serializers
from .models import Shipment, Bid, UserProfile, Vehicle
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """User serializer for basic user info"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """UserProfile serializer"""
    user = UserSerializer(read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'firebase_uid', 'user_type', 'user_type_display',
            'phone_number', 'iban', 'company_name', 'tax_id', 'billing_address',
            'service_areas', 'working_hours', 'bio',
            'rating_avg', 'rating_count',
            'profile_completed', 'documents_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rating_avg', 'rating_count', 'documents_verified', 'created_at', 'updated_at']


class VehicleSerializer(serializers.ModelSerializer):
    """Vehicle serializer"""
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'carrier_profile', 'plate_number', 'brand', 'model', 'year',
            'vehicle_type', 'vehicle_type_display', 'max_weight_kg', 'max_volume_m3',
            'has_cargo_insurance', 'insurance_company', 'insurance_expiry',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BidSerializer(serializers.ModelSerializer):
    """Bid serializer for API"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    carrier_name = serializers.CharField(read_only=True)
    carrier_email = serializers.EmailField(read_only=True)

    class Meta:
        model = Bid
        fields = [
            'bid_id', 'shipment', 'tracking_number',
            'carrier_uid', 'carrier_email', 'carrier_name', 'carrier_phone', 'carrier_verified',
            'shipper_uid', 'shipper_email',
            'offered_price', 'estimated_delivery_days', 'message', 'shipper_comment',
            'status', 'status_display',
            'created_at', 'updated_at', 'accepted_at'
        ]
        read_only_fields = ['bid_id', 'carrier_email', 'carrier_name', 'shipper_email', 'created_at', 'updated_at']


class BidCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bids"""

    class Meta:
        model = Bid
        fields = ['shipment', 'offered_price', 'estimated_delivery_days', 'message']

    def validate(self, data):
        """Validate bid data"""
        # Check if user is authenticated
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        # Check if user has profile
        if not hasattr(request.user, 'profile'):
            raise serializers.ValidationError("User profile not found")

        profile = request.user.profile

        # Check if user is a carrier
        if profile.user_type != 1:
            raise serializers.ValidationError("Only carriers can submit bids")

        # Check if user already bid on this shipment
        shipment = data['shipment']
        existing_bid = Bid.objects.filter(
            shipment=shipment,
            carrier=profile
        ).exists()

        if existing_bid:
            raise serializers.ValidationError("You have already submitted a bid for this shipment")

        return data

    def create(self, validated_data):
        """Create bid with user info"""
        import uuid
        request = self.context.get('request')
        profile = request.user.profile
        shipment = validated_data['shipment']

        # Create bid
        bid = Bid.objects.create(
            bid_id=str(uuid.uuid4()),
            shipment=shipment,
            tracking_number=shipment.tracking_number,
            carrier=profile,
            carrier_uid=str(profile.id),
            carrier_email=request.user.email,
            carrier_name=request.user.get_full_name() or request.user.username,
            carrier_phone=profile.phone_number or '',
            carrier_verified=profile.documents_verified,
            shipper_uid=str(shipment.shipper.id),
            shipper_email=shipment.shipper_email,
            offered_price=validated_data['offered_price'],
            estimated_delivery_days=validated_data['estimated_delivery_days'],
            message=validated_data.get('message', ''),
            status='pending'
        )

        # Update shipment bid count
        shipment.bid_count = shipment.bids.count()
        shipment.save(update_fields=['bid_count'])

        return bid


class ShipmentSerializer(serializers.ModelSerializer):
    """Shipment serializer for API"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cargo_type_display = serializers.CharField(source='get_cargo_type_display', read_only=True)
    shipper_name = serializers.CharField(source='shipper.user.get_full_name', read_only=True)
    bids = BidSerializer(many=True, read_only=True)
    active_bids_count = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            'shipment_id', 'tracking_number',
            'shipper', 'shipper_uid', 'shipper_email', 'shipper_phone', 'shipper_name',
            'title', 'description', 'cargo_type', 'cargo_type_display',
            'from_address_city', 'from_address_district', 'from_address_full',
            'from_address_lat', 'from_address_lng',
            'to_address_city', 'to_address_district', 'to_address_full',
            'to_address_lat', 'to_address_lng',
            'weight', 'volume',
            'suggested_price', 'final_price',
            'pickup_date', 'delivery_date',
            'images',
            'status', 'status_display',
            'assigned_carrier_uid', 'assigned_bid_id',
            'view_count', 'bid_count', 'active_bids_count',
            'bids',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'shipment_id', 'tracking_number', 'shipper_email', 'shipper_phone',
            'view_count', 'bid_count', 'created_at', 'updated_at'
        ]

    def get_active_bids_count(self, obj):
        """Get count of pending bids"""
        return obj.bids.filter(status='pending').count()


class ShipmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing shipments"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cargo_type_display = serializers.CharField(source='get_cargo_type_display', read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'shipment_id', 'tracking_number',
            'title', 'cargo_type', 'cargo_type_display',
            'from_address_city', 'from_address_district',
            'to_address_city', 'to_address_district',
            'weight', 'suggested_price',
            'pickup_date',
            'status', 'status_display',
            'view_count', 'bid_count',
            'created_at'
        ]


class ShipmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating shipments"""

    class Meta:
        model = Shipment
        fields = [
            'title', 'description', 'cargo_type',
            'from_address_city', 'from_address_district', 'from_address_full',
            'from_address_lat', 'from_address_lng',
            'to_address_city', 'to_address_district', 'to_address_full',
            'to_address_lat', 'to_address_lng',
            'weight', 'volume',
            'suggested_price',
            'pickup_date',
            'images'
        ]

    def validate(self, data):
        """Validate shipment data"""
        # Check if user is authenticated
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        # Check if user has profile
        if not hasattr(request.user, 'profile'):
            raise serializers.ValidationError("User profile not found")

        return data

    def create(self, validated_data):
        """Create shipment with user info"""
        import uuid
        from datetime import datetime

        request = self.context.get('request')
        profile = request.user.profile

        # Generate tracking number
        year = datetime.now().year
        month = datetime.now().month
        # Get count of shipments this month
        month_count = Shipment.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count() + 1

        tracking_number = f"YN-{year}-{month:02d}{month_count:04d}"

        # Create shipment
        shipment = Shipment.objects.create(
            shipment_id=str(uuid.uuid4()),
            tracking_number=tracking_number,
            shipper=profile,
            shipper_uid=str(profile.id),
            shipper_email=request.user.email,
            shipper_phone=profile.phone_number or '',
            **validated_data
        )

        return shipment
