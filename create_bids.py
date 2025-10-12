#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create test bids for shipments
"""
import os
import sys
import django
from datetime import timedelta
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nakliyenet.settings')
django.setup()

from website.models import UserProfile, Shipment, Bid
from django.utils import timezone

# Update mehmet and ahmet to be carriers
print('Setting up carriers...')
for username in ['mehmet', 'ahmet']:
    try:
        profile = UserProfile.objects.get(user__username=username)
        profile.user_type = 1  # Carrier
        profile.documents_verified = True
        if not profile.firebase_uid:
            profile.firebase_uid = f'test-{username}-uid'
        profile.save()
        print(f'  {username} -> carrier (verified)')
    except UserProfile.DoesNotExist:
        print(f'  {username} not found')

# Get carriers
carriers = list(UserProfile.objects.filter(user_type=1, documents_verified=True))
print(f'\nFound {len(carriers)} verified carriers')

# Get active shipments
shipments = list(Shipment.objects.filter(status='active').order_by('created_at'))
print(f'Found {len(shipments)} active shipments')

# Create bids
bid_messages = [
    'Bu isi yapabilirim. Profesyonel ekiple hizmetinizdeyiz.',
    'Uygun fiyat ve kaliteli hizmet. Detaylar icin ulasabilirsiniz.',
    'Alaninda uzman ekip. Garantili tasima hizmeti.',
    'Tam donanim ve sigorta ile calismaktayiz.',
]

created_bids = 0
for i, shipment in enumerate(shipments[:6]):  # First 6 shipments
    # Each shipment gets 2-3 bids
    num_bids = 2 if i % 2 == 0 else 3

    for j in range(num_bids):
        carrier = carriers[j % len(carriers)]

        # Check if bid already exists
        if Bid.objects.filter(shipment=shipment, carrier_uid=carrier.firebase_uid).exists():
            continue

        # Price variation: -10% to +5% of suggested price
        price_factor = 0.90 + (j * 0.05)
        offered_price = float(shipment.suggested_price) * price_factor

        bid = Bid.objects.create(
            bid_id=str(uuid.uuid4()),
            shipment=shipment,
            tracking_number=shipment.tracking_number,
            carrier_uid=carrier.firebase_uid,
            carrier_email=carrier.user.email or f'{carrier.user.username}@test.com',
            carrier_name=carrier.user.get_full_name() or carrier.user.username,
            carrier_phone=carrier.phone_number or '+905001234567',
            carrier_verified=carrier.documents_verified,
            shipper_uid=shipment.shipper_uid,
            shipper_email=shipment.shipper_email,
            offered_price=offered_price,
            estimated_delivery_days=2 + (j % 3),
            message=bid_messages[j % len(bid_messages)],
            status='pending',
            created_at=timezone.now() - timedelta(hours=j*6),
            updated_at=timezone.now() - timedelta(hours=j*6),
        )
        created_bids += 1

    # Update bid count
    shipment.bid_count = shipment.bids.count()
    shipment.save(update_fields=['bid_count'])

print(f'\nCreated {created_bids} bids')
print('Done!')
