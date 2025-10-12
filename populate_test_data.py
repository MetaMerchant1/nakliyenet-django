#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to populate test data for nakliyenet
"""
import os
import sys
import django
from datetime import datetime, timedelta
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nakliyenet.settings')
django.setup()

from django.contrib.auth.models import User
from website.models import UserProfile, Shipment, Bid
from django.utils import timezone

def create_test_users():
    """Create test users"""
    users_data = [
        ('mehmet', 'Mehmet', 'Yilmaz', 'mehmet@test.com', 1),
        ('ahmet', 'Ahmet', 'Kaya', 'ahmet@test.com', 1),
        ('ayse', 'Ayse', 'Demir', 'ayse@test.com', 0),
        ('fatma', 'Fatma', 'Celik', 'fatma@test.com', 0),
    ]

    created_users = []
    for username, first, last, email, user_type in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first, 'last_name': last, 'email': email}
        )
        if created or not user.password:
            user.set_password('test123')
            user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'firebase_uid': f'test-{username}-uid',
                'user_type': user_type,
                'phone_number': f'+905{ord(username[0]) % 10}{ord(username[1]) % 10}1234567',
                'company_name': f'{first} Nakliyat' if user_type == 1 else '',
                'documents_verified': user_type == 1,
            }
        )

        # Update firebase_uid if missing
        if not profile.firebase_uid:
            profile.firebase_uid = f'test-{username}-uid'
            profile.save()

        created_users.append(profile)

    print(f'Created/Updated {len(created_users)} users')
    return created_users

def create_test_shipments():
    """Create test shipments"""
    # Get shipper profiles
    shippers = list(UserProfile.objects.filter(user_type=0))
    if not shippers:
        # Use testuser as shipper
        user = User.objects.get(username='testuser')
        shippers = [user.profile]

    # Ensure all shippers have firebase_uid
    for shipper in shippers:
        if not shipper.firebase_uid:
            shipper.firebase_uid = f'test-{shipper.user.username}-uid'
            shipper.save()

    # Shipment data
    shipments_data = [
        {
            'title': 'Evden Eve Nakliyat - 3+1 Daire',
            'from_city': 'Istanbul', 'from_district': 'Kadikoy',
            'to_city': 'Ankara', 'to_district': 'Cankaya',
            'cargo_type': 'evden_eve',
            'description': '3+1 daire tam esya tasinacak. Ambalaj hizmeti gerekli.',
            'suggested_price': 8500,
            'status': 'active',
        },
        {
            'title': 'Ofis Tasima - 50m2 Ofis',
            'from_city': 'Istanbul', 'from_district': 'Besiktas',
            'to_city': 'Izmir', 'to_district': 'Karsiyaka',
            'cargo_type': 'isyeri',
            'description': 'Ofis esyalari, bilgisayarlar ve dosya dolaplari.',
            'suggested_price': 6500,
            'status': 'active',
        },
        {
            'title': 'Beyaz Esya Tasima',
            'from_city': 'Ankara', 'from_district': 'Kizilay',
            'to_city': 'Antalya', 'to_district': 'Muratpasa',
            'cargo_type': 'beyaz_esya',
            'description': 'Buzdolabi, camasir makinesi ve bulasik makinesi tasinacak.',
            'suggested_price': 3500,
            'status': 'active',
        },
        {
            'title': 'Mobilya Nakliyesi',
            'from_city': 'Izmir', 'from_district': 'Bornova',
            'to_city': 'Istanbul', 'to_district': 'Uskudar',
            'cargo_type': 'mobilya',
            'description': 'Koltuk takimi, yemek masasi ve yatak odasi takimi.',
            'suggested_price': 4500,
            'status': 'active',
        },
        {
            'title': 'Evden Eve Tam Tasinma',
            'from_city': 'Bursa', 'from_district': 'Nilufer',
            'to_city': 'Eskisehir', 'to_district': 'Tepebasi',
            'cargo_type': 'evden_eve',
            'description': '2+1 daire tam esya. Asansorlu bina.',
            'suggested_price': 5500,
            'status': 'active',
        },
        {
            'title': 'Arac Ici Esya Tasima',
            'from_city': 'Antalya', 'from_district': 'Konyaalti',
            'to_city': 'Ankara', 'to_district': 'Kecioren',
            'cargo_type': 'arac_ici',
            'description': 'Kisisel esyalar, kucuk mobilyalar.',
            'suggested_price': 2500,
            'status': 'active',
        },
        {
            'title': 'Ticari Esya Nakliyesi',
            'from_city': 'Istanbul', 'from_district': 'Sisli',
            'to_city': 'Bursa', 'to_district': 'Osmangazi',
            'cargo_type': 'isyeri',
            'description': 'Dukkandan magazaya esya tasima.',
            'suggested_price': 4000,
            'status': 'active',
        },
        {
            'title': 'Villa Esya Tasima',
            'from_city': 'Bodrum', 'from_district': 'Merkez',
            'to_city': 'Istanbul', 'to_district': 'Sariyer',
            'cargo_type': 'evden_eve',
            'description': 'Yazlik villadan tam esya nakliyesi.',
            'suggested_price': 12000,
            'status': 'active',
        },
    ]

    created_shipments = []
    for i, data in enumerate(shipments_data):
        shipper = shippers[i % len(shippers)]

        shipment_id = str(uuid.uuid4())
        tracking_number = f'YN-2025-TEST{str(i+2).zfill(2)}'

        # Check if already exists
        if Shipment.objects.filter(tracking_number=tracking_number).exists():
            print(f'Skipping {tracking_number} - already exists')
            continue

        shipment = Shipment.objects.create(
            shipment_id=shipment_id,
            tracking_number=tracking_number,
            shipper=shipper,
            shipper_uid=shipper.firebase_uid,
            shipper_email=shipper.user.email or f'{shipper.user.username}@test.com',
            shipper_phone=shipper.phone_number or '+905001234567',
            title=data['title'],
            description=data['description'],
            cargo_type=data['cargo_type'],
            from_address_city=data['from_city'],
            from_address_district=data['from_district'],
            from_address_full='Test Mahallesi, Test Sokak No:1',
            to_address_city=data['to_city'],
            to_address_district=data['to_district'],
            to_address_full='Test Mahallesi, Test Sokak No:2',
            weight=500 + (i * 100),  # Weight in kg: 500, 600, 700, etc.
            volume=2.0 + (i * 0.5),  # Volume in m³
            suggested_price=data['suggested_price'],
            status=data['status'],
            pickup_date=timezone.now().date() + timedelta(days=i+3),
            created_at=timezone.now() - timedelta(days=i),
            updated_at=timezone.now() - timedelta(days=i),
        )
        created_shipments.append(shipment)

    print(f'Created {len(created_shipments)} shipments')
    return created_shipments

def create_test_bids():
    """Create test bids"""
    # Get carriers
    carriers = list(UserProfile.objects.filter(user_type=1, documents_verified=True))
    if not carriers:
        print('No verified carriers found')
        return []

    # Get active shipments
    shipments = list(Shipment.objects.filter(status='active'))

    created_bids = []
    bid_messages = [
        'Bu isi yapabilirim. Profesyonel ekiple hizmetinizdeyiz.',
        'Uygun fiyat ve kaliteli hizmet. Detaylar icin ulasabilirsiniz.',
        'Alaninda uzman ekip. Garantili tasima hizmeti.',
        'Tam donanim ve sigorta ile calismaktayiz.',
    ]

    for i, shipment in enumerate(shipments[:6]):  # First 6 shipments get bids
        # Each shipment gets 2-3 bids
        num_bids = 2 if i % 2 == 0 else 3

        for j in range(num_bids):
            carrier = carriers[j % len(carriers)]

            # Check if bid already exists
            if Bid.objects.filter(shipment=shipment, carrier_uid=carrier.firebase_uid).exists():
                continue

            # Price variation: -10% to +5% of suggested price
            price_factor = 0.90 + (j * 0.05)
            offered_price = int(shipment.suggested_price * price_factor)

            bid = Bid.objects.create(
                bid_id=str(uuid.uuid4()),
                shipment=shipment,
                tracking_number=shipment.tracking_number,
                carrier=carrier,
                carrier_uid=carrier.firebase_uid,
                shipper_uid=shipment.shipper_uid,
                offered_price=offered_price,
                message=bid_messages[j % len(bid_messages)],
                status='pending',
                created_at=timezone.now() - timedelta(hours=j*6),
                updated_at=timezone.now() - timedelta(hours=j*6),
            )
            created_bids.append(bid)

        # Update bid count
        shipment.bid_count = shipment.bids.count()
        shipment.save(update_fields=['bid_count'])

    print(f'Created {len(created_bids)} bids')
    return created_bids

if __name__ == '__main__':
    print('Populating test data...')
    print('')

    users = create_test_users()
    print('')

    shipments = create_test_shipments()
    print('')

    bids = create_test_bids()
    print('')

    print('Done!')
    print(f'Total: {len(users)} users, {len(shipments)} shipments, {len(bids)} bids')
