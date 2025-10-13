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
from website.models import UserProfile, Shipment, Bid, ShipmentTracking, DeliveryProof, Review
from django.utils import timezone
from decimal import Decimal

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
                'user_type': user_type,
                'phone_number': f'+905{ord(username[0]) % 10}{ord(username[1]) % 10}1234567',
                'company_name': f'{first} Nakliyat' if user_type == 1 else '',
            }
        )

        created_users.append(profile)

    print(f'Created/Updated {len(created_users)} users')
    return created_users

def create_test_shipments():
    """Create test shipments"""
    # Get shipper profiles
    shippers = list(UserProfile.objects.filter(user_type=0))
    if not shippers:
        # Create a default shipper if none exist
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'testuser@test.com'}
        )
        if created or not hasattr(user, 'profile'):
            profile = UserProfile.objects.create(
                user=user,
                user_type=0,
                phone_number='+905001234567'
            )
            shippers = [profile]
        else:
            shippers = [user.profile]

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
    carriers = list(UserProfile.objects.filter(user_type=1))
    if not carriers:
        print('No carriers found')
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
            if Bid.objects.filter(shipment=shipment, carrier=carrier).exists():
                continue

            # Price variation: -10% to +5% of suggested price
            price_factor = Decimal('0.90') + (Decimal(j) * Decimal('0.05'))
            offered_price = int(shipment.suggested_price * price_factor)

            bid = Bid.objects.create(
                bid_id=str(uuid.uuid4()),
                shipment=shipment,
                tracking_number=shipment.tracking_number,
                carrier=carrier,
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

def create_accepted_shipments():
    """Accept some bids and create shipments in different stages"""
    # Get some pending bids
    pending_bids = list(Bid.objects.filter(status='pending')[:4])

    if not pending_bids:
        print('No pending bids found to accept')
        return []

    accepted_shipments = []
    statuses = ['assigned', 'picked_up', 'in_transit', 'delivered']

    for i, bid in enumerate(pending_bids):
        # Accept the bid
        bid.status = 'accepted'
        bid.accepted_at = timezone.now() - timedelta(days=i+1)
        bid.save()

        # Update shipment
        shipment = bid.shipment
        shipment.status = statuses[i % len(statuses)]
        shipment.assigned_bid_id = bid.bid_id
        shipment.final_price = bid.offered_price
        shipment.save()

        # Reject other bids for this shipment
        Bid.objects.filter(shipment=shipment, status='pending').exclude(bid_id=bid.bid_id).update(
            status='rejected',
            rejected_at=timezone.now() - timedelta(days=i+1)
        )

        accepted_shipments.append(shipment)

    print(f'Accepted {len(accepted_shipments)} bids and updated shipments')
    return accepted_shipments

def create_tracking_updates():
    """Create tracking updates for shipments with accepted bids"""
    # Get shipments with assigned status or later
    shipments = Shipment.objects.filter(status__in=['assigned', 'picked_up', 'in_transit', 'delivered'])

    created_tracking = []

    # Turkish cities for location tracking
    cities = ['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya']

    for shipment in shipments:
        carrier = shipment.bids.filter(status='accepted').first()
        if not carrier:
            continue

        carrier_profile = carrier.carrier

        # Status progression based on current status
        status_progression = {
            'assigned': ['assigned'],
            'picked_up': ['assigned', 'picked_up'],
            'in_transit': ['assigned', 'picked_up', 'in_transit'],
            'delivered': ['assigned', 'picked_up', 'in_transit', 'delivered'],
        }

        statuses = status_progression.get(shipment.status, ['assigned'])

        for idx, status in enumerate(statuses):
            status_displays = {
                'assigned': 'Taşıyıcı atandı',
                'picked_up': f'Yük {shipment.from_address_city} lokasyonundan toplandı',
                'in_transit': f'Yük yolda - {cities[idx % len(cities)]} geçiş noktası',
                'delivered': f'Yük {shipment.to_address_city} adresine teslim edildi',
            }

            notes = {
                'assigned': 'Taşıyıcı başarıyla atandı. Yük toplama işlemi için hazırlıklar başladı.',
                'picked_up': 'Yük başarıyla toplandı. Ambalaj ve yükleme tamamlandı.',
                'in_transit': 'Yük güvenli bir şekilde yolda. Tahmini varış zamanı takip ediliyor.',
                'delivered': 'Yük başarıyla teslim edildi. Teslimat onayı bekleniyor.',
            }

            # Check if tracking already exists
            if ShipmentTracking.objects.filter(shipment=shipment, status=status).exists():
                continue

            tracking = ShipmentTracking.objects.create(
                shipment=shipment,
                status=status,
                status_display=status_displays[status],
                location=cities[idx % len(cities)] if status in ['picked_up', 'in_transit', 'delivered'] else '',
                note=notes[status],
                updated_by=carrier_profile,
                is_automatic=False,
                created_at=timezone.now() - timedelta(days=len(statuses)-idx, hours=idx*6)
            )
            created_tracking.append(tracking)

    print(f'Created {len(created_tracking)} tracking updates')
    return created_tracking

def create_delivery_proofs():
    """Create delivery proof for delivered shipments"""
    # Get delivered shipments
    delivered_shipments = Shipment.objects.filter(status='delivered')

    created_proofs = []

    # Sample proof URLs (you can replace with real Firebase URLs)
    sample_photo_urls = [
        'https://via.placeholder.com/800x600/4CAF50/FFFFFF?text=Delivered+Package+1',
        'https://via.placeholder.com/800x600/2196F3/FFFFFF?text=Delivered+Package+2',
        'https://via.placeholder.com/800x600/FF9800/FFFFFF?text=Delivered+Package+3',
    ]

    sample_signature_urls = [
        'https://via.placeholder.com/400x200/9C27B0/FFFFFF?text=Signature+1',
        'https://via.placeholder.com/400x200/E91E63/FFFFFF?text=Signature+2',
    ]

    descriptions = [
        'Yük hasarsız teslim edildi. Tüm eşyalar eksiksiz.',
        'Müşteri eşyalarını kontrol etti ve onayladı.',
        'Teslimat tamamlandı. Müşteri memnuniyeti sağlandı.',
    ]

    for i, shipment in enumerate(delivered_shipments):
        carrier = shipment.bids.filter(status='accepted').first()
        if not carrier:
            continue

        # Check if proof already exists
        if DeliveryProof.objects.filter(shipment=shipment).exists():
            continue

        # Create photo proof from carrier
        photo_proof = DeliveryProof.objects.create(
            shipment=shipment,
            uploaded_by=carrier.carrier,
            is_shipper=False,
            proof_type='photo',
            file_url=sample_photo_urls[i % len(sample_photo_urls)],
            description=descriptions[i % len(descriptions)],
            created_at=timezone.now() - timedelta(hours=2)
        )
        created_proofs.append(photo_proof)

        # Create signature proof from shipper
        signature_proof = DeliveryProof.objects.create(
            shipment=shipment,
            uploaded_by=shipment.shipper,
            is_shipper=True,
            proof_type='signature',
            file_url=sample_signature_urls[i % len(sample_signature_urls)],
            description='Teslimatı onaylıyorum.',
            created_at=timezone.now() - timedelta(hours=1)
        )
        created_proofs.append(signature_proof)

    print(f'Created {len(created_proofs)} delivery proofs')
    return created_proofs

def create_reviews():
    """Create reviews for delivered shipments"""
    # Get delivered shipments
    delivered_shipments = Shipment.objects.filter(status='delivered')

    created_reviews = []

    # Sample review comments
    shipper_comments = [
        'Çok profesyonel bir hizmet aldık. Eşyalarımız hasarsız teslim edildi. Teşekkürler!',
        'Zamanında ve güvenli teslimat. Taşıma sırasında çok dikkatli davrandılar.',
        'Mükemmel bir deneyimdi. Hem fiyat hem de kalite açısından çok memnun kaldık.',
        'İletişim çok iyiydi. Her aşamada bilgilendirdiler. Kesinlikle tavsiye ederim.',
    ]

    carrier_comments = [
        'Çok düzenli ve iyi iletişim kuran bir müşteri. İşbirliği yapmak keyifliydi.',
        'Zamanında hazır olan ve tüm detayları önceden bildiren bir müşteri. Teşekkürler!',
        'Profesyonel ve anlayışlı bir müşteri. Tekrar çalışmaktan memnuniyet duyarız.',
        'Her şey planlandığı gibi gitti. Güzel bir çalışmaydı.',
    ]

    for i, shipment in enumerate(delivered_shipments):
        accepted_bid = shipment.bids.filter(status='accepted').first()
        if not accepted_bid:
            continue

        carrier = accepted_bid.carrier
        shipper = shipment.shipper

        # Check if reviews already exist
        if Review.objects.filter(shipment=shipment).exists():
            continue

        # Shipper reviews carrier
        shipper_review = Review.objects.create(
            shipment=shipment,
            bid=accepted_bid,
            reviewer=shipper,
            reviewed=carrier,
            rating=4 + (i % 2),  # 4 or 5 stars
            communication_rating=4 + (i % 2),
            professionalism_rating=5,
            punctuality_rating=4 + ((i+1) % 2),
            comment=shipper_comments[i % len(shipper_comments)],
            is_shipper_review=True,
            is_visible=True,
            created_at=timezone.now() - timedelta(hours=12-i)
        )
        created_reviews.append(shipper_review)

        # Carrier reviews shipper
        carrier_review = Review.objects.create(
            shipment=shipment,
            bid=accepted_bid,
            reviewer=carrier,
            reviewed=shipper,
            rating=4 + ((i+1) % 2),  # 4 or 5 stars
            communication_rating=5,
            professionalism_rating=4 + (i % 2),
            punctuality_rating=5,
            comment=carrier_comments[i % len(carrier_comments)],
            is_shipper_review=False,
            is_visible=True,
            created_at=timezone.now() - timedelta(hours=10-i)
        )
        created_reviews.append(carrier_review)

    print(f'Created {len(created_reviews)} reviews')
    return created_reviews

if __name__ == '__main__':
    print('=' * 60)
    print('NAKLIYENET TEST DATA POPULATION')
    print('=' * 60)
    print('')

    print('Step 1: Creating test users...')
    users = create_test_users()
    print('')

    print('Step 2: Creating test shipments...')
    shipments = create_test_shipments()
    print('')

    print('Step 3: Creating test bids...')
    bids = create_test_bids()
    print('')

    print('Step 4: Accepting some bids...')
    accepted = create_accepted_shipments()
    print('')

    print('Step 5: Creating tracking updates...')
    tracking = create_tracking_updates()
    print('')

    print('Step 6: Creating delivery proofs...')
    proofs = create_delivery_proofs()
    print('')

    print('Step 7: Creating reviews...')
    reviews = create_reviews()
    print('')

    print('=' * 60)
    print('SUMMARY')
    print('=' * 60)
    print(f'Users:            {len(users)}')
    print(f'Shipments:        {len(shipments)}')
    print(f'Bids:             {len(bids)}')
    print(f'Accepted Bids:    {len(accepted)}')
    print(f'Tracking Updates: {len(tracking)}')
    print(f'Delivery Proofs:  {len(proofs)}')
    print(f'Reviews:          {len(reviews)}')
    print('=' * 60)
    print('')
    print('Done! Test data populated successfully!')
    print('')
