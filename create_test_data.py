"""
Test verileri oluştur - Ödeme workflow'unun her aşamasında birer ilan
"""
import os
import django
import sys

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nakliyenet.settings')
django.setup()

from django.contrib.auth.models import User
from website.models import UserProfile, Shipment, Bid, Payment
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

def create_test_users():
    """Test kullanıcıları oluştur"""

    # Yük sahibi
    shipper_user, _ = User.objects.get_or_create(
        username='yukSahibi',
        defaults={
            'email': 'yuksahibi@test.com',
            'first_name': 'Ahmet',
            'last_name': 'Yılmaz'
        }
    )
    shipper_user.set_password('test123')
    shipper_user.save()

    shipper_profile, _ = UserProfile.objects.get_or_create(
        user=shipper_user,
        defaults={
            'phone_number': '0532 111 1111',
            'user_type': 0,
            'documents_verified': True,
            'profile_completed': True
        }
    )
    shipper_profile.firebase_uid = shipper_profile.firebase_uid or f'shipper_{uuid.uuid4().hex[:8]}'
    shipper_profile.save()

    # Taşıyıcı 1
    carrier1_user, _ = User.objects.get_or_create(
        username='tasiyici1',
        defaults={
            'email': 'tasiyici1@test.com',
            'first_name': 'Mehmet',
            'last_name': 'Demir'
        }
    )
    carrier1_user.set_password('test123')
    carrier1_user.save()

    carrier1_profile, _ = UserProfile.objects.get_or_create(
        user=carrier1_user,
        defaults={
            'phone_number': '0532 222 2222',
            'user_type': 1,
            'documents_verified': True,
            'profile_completed': True
        }
    )
    carrier1_profile.firebase_uid = carrier1_profile.firebase_uid or f'carrier1_{uuid.uuid4().hex[:8]}'
    carrier1_profile.save()

    # Taşıyıcı 2
    carrier2_user, _ = User.objects.get_or_create(
        username='tasiyici2',
        defaults={
            'email': 'tasiyici2@test.com',
            'first_name': 'Ali',
            'last_name': 'Kaya'
        }
    )
    carrier2_user.set_password('test123')
    carrier2_user.save()

    carrier2_profile, _ = UserProfile.objects.get_or_create(
        user=carrier2_user,
        defaults={
            'phone_number': '0532 333 3333',
            'user_type': 1,
            'documents_verified': True,
            'profile_completed': True
        }
    )
    carrier2_profile.firebase_uid = carrier2_profile.firebase_uid or f'carrier2_{uuid.uuid4().hex[:8]}'
    carrier2_profile.save()

    # Taşıyıcı 3
    carrier3_user, _ = User.objects.get_or_create(
        username='tasiyici3',
        defaults={
            'email': 'tasiyici3@test.com',
            'first_name': 'Veli',
            'last_name': 'Şahin'
        }
    )
    carrier3_user.set_password('test123')
    carrier3_user.save()

    carrier3_profile, _ = UserProfile.objects.get_or_create(
        user=carrier3_user,
        defaults={
            'phone_number': '0532 444 4444',
            'user_type': 1,
            'documents_verified': True,
            'profile_completed': True
        }
    )
    carrier3_profile.firebase_uid = carrier3_profile.firebase_uid or f'carrier3_{uuid.uuid4().hex[:8]}'
    carrier3_profile.save()

    return shipper_profile, carrier1_profile, carrier2_profile, carrier3_profile

def create_stage_1_pending_payment(shipper, carrier):
    """Aşama 1: Teklif kabul edildi, ödeme bekliyor"""

    shipment = Shipment.objects.create(
        shipment_id=str(uuid.uuid4()),
        tracking_number=f'YN-2025-{uuid.uuid4().hex[:6].upper()}',
        shipper=shipper,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        shipper_phone=shipper.phone_number,
        title='İstanbul - Ankara Elektronik Eşya Taşıma',
        description='Hassas elektronik eşyalar güvenli taşıma gerekiyor',
        cargo_type='elektronik',
        from_address_city='İstanbul',
        from_address_district='Kadıköy',
        from_address_full='Caferağa Mahallesi, Kadıköy, İstanbul',
        to_address_city='Ankara',
        to_address_district='Çankaya',
        to_address_full='Kızılay Meydanı, Çankaya, Ankara',
        weight=50,
        volume=2.5,
        suggested_price=2000,
        pickup_date=timezone.now() + timedelta(days=3),
        status='pending_payment',
        insurance_requested=True,
        insurance_value=5000
    )

    bid = Bid.objects.create(
        bid_id=str(uuid.uuid4()),
        shipment=shipment,
        tracking_number=shipment.tracking_number,
        carrier_uid=carrier.firebase_uid,
        carrier_email=carrier.user.email,
        carrier_name=carrier.user.get_full_name(),
        carrier_phone=carrier.phone_number,
        carrier_verified=carrier.documents_verified,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        offered_price=1800,
        estimated_delivery_days=2,
        message='Sigortalı taşıma, profesyonel ekip',
        status='accepted',
        accepted_at=timezone.now()
    )

    payment = Payment.objects.create(
        shipment=shipment,
        bid=bid,
        shipper=shipper,
        carrier=carrier,
        amount=Decimal('1800.00'),
        status='pending'
    )

    return shipment, payment

def create_stage_2_paid(shipper, carrier):
    """Aşama 2: Ödeme yapıldı, taşıyıcı yükü alacak"""

    shipment = Shipment.objects.create(
        shipment_id=str(uuid.uuid4()),
        tracking_number=f'YN-2025-{uuid.uuid4().hex[:6].upper()}',
        shipper=shipper,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        shipper_phone=shipper.phone_number,
        title='İzmir - Bursa Mobilya Taşıma',
        description='Ev eşyası ve mobilya taşınması',
        cargo_type='mobilya',
        from_address_city='İzmir',
        from_address_district='Karşıyaka',
        from_address_full='Bostanlı Mahallesi, Karşıyaka, İzmir',
        to_address_city='Bursa',
        to_address_district='Nilüfer',
        to_address_full='Görükle Kampüsü, Nilüfer, Bursa',
        weight=300,
        volume=15,
        suggested_price=3500,
        pickup_date=timezone.now() + timedelta(days=2),
        status='assigned',
        insurance_requested=True,
        insurance_value=10000
    )

    bid = Bid.objects.create(
        bid_id=str(uuid.uuid4()),
        shipment=shipment,
        tracking_number=shipment.tracking_number,
        carrier_uid=carrier.firebase_uid,
        carrier_email=carrier.user.email,
        carrier_name=carrier.user.get_full_name(),
        carrier_phone=carrier.phone_number,
        carrier_verified=carrier.documents_verified,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        offered_price=3200,
        estimated_delivery_days=1,
        message='Profesyonel mobilya taşıma ekibi',
        status='accepted',
        accepted_at=timezone.now() - timedelta(hours=2)
    )

    payment = Payment.objects.create(
        shipment=shipment,
        bid=bid,
        shipper=shipper,
        carrier=carrier,
        amount=Decimal('3200.00'),
        status='paid',
        paid_at=timezone.now() - timedelta(hours=1),
        transaction_id=f'TXN-{uuid.uuid4().hex[:12].upper()}',
        payment_provider='Test Provider'
    )

    return shipment, payment

def create_stage_3_in_transit(shipper, carrier):
    """Aşama 3: Yük yolda, teslim bekliyor"""

    shipment = Shipment.objects.create(
        shipment_id=str(uuid.uuid4()),
        tracking_number=f'YN-2025-{uuid.uuid4().hex[:6].upper()}',
        shipper=shipper,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        shipper_phone=shipper.phone_number,
        title='Antalya - İstanbul Tekstil Ürünleri',
        description='Toptan tekstil ürünleri nakliyesi',
        cargo_type='tekstil',
        from_address_city='Antalya',
        from_address_district='Muratpaşa',
        from_address_full='Lara Bölgesi, Muratpaşa, Antalya',
        to_address_city='İstanbul',
        to_address_district='Beyoğlu',
        to_address_full='Taksim, Beyoğlu, İstanbul',
        weight=200,
        volume=10,
        suggested_price=2500,
        pickup_date=timezone.now() - timedelta(days=1),
        status='in_transit',
        insurance_requested=False
    )

    bid = Bid.objects.create(
        bid_id=str(uuid.uuid4()),
        shipment=shipment,
        tracking_number=shipment.tracking_number,
        carrier_uid=carrier.firebase_uid,
        carrier_email=carrier.user.email,
        carrier_name=carrier.user.get_full_name(),
        carrier_phone=carrier.phone_number,
        carrier_verified=carrier.documents_verified,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        offered_price=2300,
        estimated_delivery_days=1,
        message='Hızlı teslimat garantisi',
        status='accepted',
        accepted_at=timezone.now() - timedelta(days=2)
    )

    payment = Payment.objects.create(
        shipment=shipment,
        bid=bid,
        shipper=shipper,
        carrier=carrier,
        amount=Decimal('2300.00'),
        status='in_transit',
        paid_at=timezone.now() - timedelta(days=2),
        transaction_id=f'TXN-{uuid.uuid4().hex[:12].upper()}',
        payment_provider='Test Provider',
        carrier_confirmed_delivery=True,
        carrier_confirmed_at=timezone.now() - timedelta(days=1)
    )

    return shipment, payment

def create_stage_4_delivered(shipper, carrier):
    """Aşama 4: Her iki taraf onayladı, admin transfer edecek"""

    shipment = Shipment.objects.create(
        shipment_id=str(uuid.uuid4()),
        tracking_number=f'YN-2025-{uuid.uuid4().hex[:6].upper()}',
        shipper=shipper,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        shipper_phone=shipper.phone_number,
        title='Bursa - Adana Gıda Ürünleri',
        description='Paketlenmiş gıda ürünleri soğuk zincir',
        cargo_type='gida',
        from_address_city='Bursa',
        from_address_district='Osmangazi',
        from_address_full='Merkez, Osmangazi, Bursa',
        to_address_city='Adana',
        to_address_district='Seyhan',
        to_address_full='Çınarlı, Seyhan, Adana',
        weight=500,
        volume=25,
        suggested_price=4500,
        pickup_date=timezone.now() - timedelta(days=3),
        status='delivered',
        insurance_requested=True,
        insurance_value=15000,
        completed_at=timezone.now() - timedelta(hours=2)
    )

    bid = Bid.objects.create(
        bid_id=str(uuid.uuid4()),
        shipment=shipment,
        tracking_number=shipment.tracking_number,
        carrier_uid=carrier.firebase_uid,
        carrier_email=carrier.user.email,
        carrier_name=carrier.user.get_full_name(),
        carrier_phone=carrier.phone_number,
        carrier_verified=carrier.documents_verified,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        offered_price=4200,
        estimated_delivery_days=2,
        message='Soğuk zincir taşımacılık',
        status='accepted',
        accepted_at=timezone.now() - timedelta(days=4)
    )

    payment = Payment.objects.create(
        shipment=shipment,
        bid=bid,
        shipper=shipper,
        carrier=carrier,
        amount=Decimal('4200.00'),
        status='delivered',
        paid_at=timezone.now() - timedelta(days=4),
        transaction_id=f'TXN-{uuid.uuid4().hex[:12].upper()}',
        payment_provider='Test Provider',
        shipper_confirmed_delivery=True,
        shipper_confirmed_at=timezone.now() - timedelta(hours=3),
        carrier_confirmed_delivery=True,
        carrier_confirmed_at=timezone.now() - timedelta(hours=2)
    )

    return shipment, payment

def create_stage_5_completed(shipper, carrier):
    """Aşama 5: Admin transfer etti, iş bitti"""

    # Admin kullanıcısı
    try:
        admin_user = User.objects.get(is_superuser=True)
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@nakliyenet.com',
            password='admin123'
        )

    shipment = Shipment.objects.create(
        shipment_id=str(uuid.uuid4()),
        tracking_number=f'YN-2025-{uuid.uuid4().hex[:6].upper()}',
        shipper=shipper,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        shipper_phone=shipper.phone_number,
        title='Ankara - İzmir Makine Parçaları',
        description='Endüstriyel makine parçaları taşıma',
        cargo_type='makine',
        from_address_city='Ankara',
        from_address_district='Yenimahalle',
        from_address_full='Organize Sanayi Bölgesi, Yenimahalle, Ankara',
        to_address_city='İzmir',
        to_address_district='Bornova',
        to_address_full='Ege Sanayi Sitesi, Bornova, İzmir',
        weight=800,
        volume=40,
        suggested_price=6000,
        pickup_date=timezone.now() - timedelta(days=7),
        status='delivered',
        insurance_requested=True,
        insurance_value=25000,
        completed_at=timezone.now() - timedelta(days=2)
    )

    bid = Bid.objects.create(
        bid_id=str(uuid.uuid4()),
        shipment=shipment,
        tracking_number=shipment.tracking_number,
        carrier_uid=carrier.firebase_uid,
        carrier_email=carrier.user.email,
        carrier_name=carrier.user.get_full_name(),
        carrier_phone=carrier.phone_number,
        carrier_verified=carrier.documents_verified,
        shipper_uid=shipper.firebase_uid,
        shipper_email=shipper.user.email,
        offered_price=5500,
        estimated_delivery_days=3,
        message='Ağır yük taşıma tecrübesi',
        status='accepted',
        accepted_at=timezone.now() - timedelta(days=8)
    )

    payment = Payment.objects.create(
        shipment=shipment,
        bid=bid,
        shipper=shipper,
        carrier=carrier,
        amount=Decimal('5500.00'),
        status='completed',
        paid_at=timezone.now() - timedelta(days=8),
        transaction_id=f'TXN-{uuid.uuid4().hex[:12].upper()}',
        payment_provider='Test Provider',
        shipper_confirmed_delivery=True,
        shipper_confirmed_at=timezone.now() - timedelta(days=3),
        carrier_confirmed_delivery=True,
        carrier_confirmed_at=timezone.now() - timedelta(days=3),
        admin_transferred=True,
        admin_transferred_by=admin_user,
        admin_transferred_at=timezone.now() - timedelta(days=2)
    )

    return shipment, payment

def main():
    print('Test verileri oluşturuluyor...\n')

    # Kullanıcıları oluştur
    print('1. Kullanıcılar oluşturuluyor...')
    shipper, carrier1, carrier2, carrier3 = create_test_users()
    print(f'   ✓ Yük Sahibi: {shipper.user.username} / {shipper.user.email}')
    print(f'   ✓ Taşıyıcı 1: {carrier1.user.username} / {carrier1.user.email}')
    print(f'   ✓ Taşıyıcı 2: {carrier2.user.username} / {carrier2.user.email}')
    print(f'   ✓ Taşıyıcı 3: {carrier3.user.username} / {carrier3.user.email}')
    print()

    # Her aşamada birer ilan oluştur
    print('2. Test ilanları oluşturuluyor...\n')

    print('   AŞAMA 1: Ödeme Bekliyor')
    s1, p1 = create_stage_1_pending_payment(shipper, carrier1)
    print(f'   ✓ İlan: {s1.tracking_number}')
    print(f'   ✓ Ödeme ID: {p1.payment_id}')
    print(f'   ✓ Durum: {p1.get_status_display()}')
    print(f'   ✓ URL: http://127.0.0.1:8000/odeme/{p1.payment_id}/')
    print()

    print('   AŞAMA 2: Ödeme Yapıldı')
    s2, p2 = create_stage_2_paid(shipper, carrier2)
    print(f'   ✓ İlan: {s2.tracking_number}')
    print(f'   ✓ Ödeme ID: {p2.payment_id}')
    print(f'   ✓ Durum: {p2.get_status_display()}')
    print(f'   ✓ URL: http://127.0.0.1:8000/ilan/{s2.tracking_number}/')
    print()

    print('   AŞAMA 3: Yük Yolda')
    s3, p3 = create_stage_3_in_transit(shipper, carrier3)
    print(f'   ✓ İlan: {s3.tracking_number}')
    print(f'   ✓ Ödeme ID: {p3.payment_id}')
    print(f'   ✓ Durum: {p3.get_status_display()}')
    print(f'   ✓ Taşıyıcı onayladı, yük sahibi onaylayacak')
    print(f'   ✓ URL: http://127.0.0.1:8000/teslim-onayla/{p3.payment_id}/')
    print()

    print('   AŞAMA 4: Teslim Edildi (Admin Transfer Edecek)')
    s4, p4 = create_stage_4_delivered(shipper, carrier1)
    print(f'   ✓ İlan: {s4.tracking_number}')
    print(f'   ✓ Ödeme ID: {p4.payment_id}')
    print(f'   ✓ Durum: {p4.get_status_display()}')
    print(f'   ✓ Her iki taraf onayladı')
    print(f'   ✓ Admin Panel: http://127.0.0.1:8000/admin/website/payment/{p4.payment_id}/change/')
    print()

    print('   AŞAMA 5: Transfer Tamamlandı')
    s5, p5 = create_stage_5_completed(shipper, carrier2)
    print(f'   ✓ İlan: {s5.tracking_number}')
    print(f'   ✓ Ödeme ID: {p5.payment_id}')
    print(f'   ✓ Durum: {p5.get_status_display()}')
    print(f'   ✓ Admin transfer etti, iş bitti')
    print()

    print('=' * 70)
    print('TEST VERİLERİ BAŞARIYLA OLUŞTURULDU!')
    print('=' * 70)
    print()
    print('Giriş Bilgileri:')
    print(f'  Yük Sahibi: yukSahibi / test123')
    print(f'  Taşıyıcı 1: tasiyici1 / test123')
    print(f'  Taşıyıcı 2: tasiyici2 / test123')
    print(f'  Taşıyıcı 3: tasiyici3 / test123')
    print(f'  Admin: admin / admin123')
    print()
    print('Test Senaryoları:')
    print(f'  1. yukSahibi ile giriş yap → İlanlarım → Ödeme yap')
    print(f'  2. tasiyici2 ile giriş yap → İlanlarım → Yükü al')
    print(f'  3. yukSahibi ile giriş yap → İlanlarım → Teslimatı onayla (AŞAMA 3)')
    print(f'  4. admin ile giriş yap → Admin Panel → Payment → Transfer yap (AŞAMA 4)')
    print()

if __name__ == '__main__':
    main()
