"""
API URL Configuration
REST API endpoints for mobile app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ShipmentViewSet, BidViewSet, UserProfileViewSet, VehicleViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'bids', BidViewSet, basename='bid')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
