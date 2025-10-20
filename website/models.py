"""
Django Models for Admin Panel
These models are used for admin verification and monitoring
Actual data is stored in Firebase Firestore (shared with mobile app)
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserDocument(models.Model):
    """
    User uploaded documents (Ehliyet, Ruhsat, SRC, Psikoteknik)
    Documents are uploaded to Firebase Storage by mobile app
    Admin verifies them here
    """
    DOCUMENT_TYPES = [
        ('license', 'Ehliyet'),
        ('registration', 'Ruhsat'),
        ('src', 'SRC Belgesi'),
        ('psychotech', 'Psikoteknik Raporu'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]

    user_email = models.EmailField(help_text="Kullanıcı email")
    user_name = models.CharField(max_length=255, blank=True)

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_url = models.URLField(help_text="Firebase Storage URL")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    rejection_reason = models.TextField(blank=True, help_text="Reddedilme sebebi")
    notes = models.TextField(blank=True, help_text="Admin notları")

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Kullanıcı Belgesi"
        verbose_name_plural = "Kullanıcı Belgeleri"
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user_email} - {self.get_document_type_display()} ({self.get_status_display()})"


class AdminActivity(models.Model):
    """
    Admin activity log
    Track all admin actions for audit
    """
    ACTION_TYPES = [
        ('document_approved', 'Belge Onaylandı'),
        ('document_rejected', 'Belge Reddedildi'),
        ('shipment_approved', 'İlan Onaylandı'),
        ('shipment_rejected', 'İlan Reddedildi'),
        ('user_suspended', 'Kullanıcı Askıya Alındı'),
        ('user_activated', 'Kullanıcı Aktif Edildi'),
    ]

    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    target_type = models.CharField(max_length=50, help_text="user, document, shipment")
    target_id = models.CharField(max_length=128)

    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Admin Aktivitesi"
        verbose_name_plural = "Admin Aktiviteleri"

    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_type_display()} - {self.timestamp}"


class UserProfile(models.Model):
    """
    User profile for web users (extends Django User)
    Synced with Firebase when documents are uploaded
    """
    USER_TYPES = [
        (0, 'Yük Veren'),      # Shipper - no documents required
        (1, 'Taşıyıcı'),       # Carrier - documents required
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # User type
    user_type = models.IntegerField(choices=USER_TYPES, default=0, help_text="Kullanıcı tipi: Yük Veren veya Taşıyıcı")

    # Contact information
    phone_number = models.CharField(max_length=20, blank=True, help_text="Telefon numarası")
    iban = models.CharField(max_length=34, blank=True, help_text="IBAN numarası (TR ile başlayan)")

    # Shipper specific fields
    company_name = models.CharField(max_length=200, blank=True, help_text="Şirket adı (opsiyonel)")
    tax_id = models.CharField(max_length=20, blank=True, help_text="Vergi/TC Kimlik Numarası")
    billing_address = models.TextField(blank=True, help_text="Fatura adresi")

    # Carrier specific fields
    service_areas = models.TextField(blank=True, help_text="Hizmet verilen şehirler (virgülle ayrılmış)")
    working_hours = models.CharField(max_length=100, blank=True, default="09:00-18:00", help_text="Çalışma saatleri")
    bio = models.TextField(blank=True, help_text="Taşıyıcı hakkında (max 500 karakter)", max_length=500)

    # Rating (calculated field)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, help_text="Ortalama puan")
    rating_count = models.IntegerField(default=0, help_text="Toplam değerlendirme sayısı")

    # Profile completion
    profile_completed = models.BooleanField(default=False)
    documents_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.user.email} - Profile"

    def get_document_count(self):
        """Get count of uploaded documents"""
        return UserDocument.objects.filter(user_email=self.user.email).count()

    def get_approved_document_count(self):
        """Get count of approved documents"""
        return UserDocument.objects.filter(user_email=self.user.email, status='approved').count()

    def check_documents_verified(self):
        """Check if all required documents are approved (only for carriers)"""
        # Yük verenler için belge gerekmez
        if self.user_type == 0:  # Shipper
            return True

        # Taşıyıcılar için tüm belgeler gerekli
        required_docs = ['license', 'registration', 'src', 'psychotech']
        for doc_type in required_docs:
            if not UserDocument.objects.filter(
                user_email=self.user.email,
                document_type=doc_type,
                status='approved'
            ).exists():
                return False
        return True

    def is_carrier(self):
        """Check if user is a carrier"""
        return self.user_type == 1

    def is_shipper(self):
        """Check if user is a shipper"""
        return self.user_type == 0


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Auto-save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Vehicle(models.Model):
    """
    Vehicle information for carriers
    One carrier can have multiple vehicles
    """
    VEHICLE_TYPES = [
        (0, 'Kamyonet'),
        (1, 'Kamyon'),
        (2, 'TIR'),
        (3, 'Çekici'),
        (4, 'Dorse'),
    ]

    carrier_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='vehicles')

    # Vehicle identification
    plate_number = models.CharField(max_length=20, unique=True, help_text="Plaka numarası (34 ABC 123)")

    # Vehicle details
    brand = models.CharField(max_length=100, help_text="Marka (Mercedes, Ford, vb)")
    model = models.CharField(max_length=100, help_text="Model")
    year = models.IntegerField(help_text="Yıl")
    vehicle_type = models.IntegerField(choices=VEHICLE_TYPES, default=0)

    # Capacity
    max_weight_kg = models.IntegerField(help_text="Maksimum yük kapasitesi (kg)")
    max_volume_m3 = models.DecimalField(max_digits=5, decimal_places=2, help_text="Maksimum hacim (m³)")

    # Insurance
    has_cargo_insurance = models.BooleanField(default=False, help_text="Nakliye sigortası var mı?")
    insurance_company = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True, help_text="Sigorta bitiş tarihi")

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Araç"
        verbose_name_plural = "Araçlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.plate_number} - {self.brand} {self.model}"


class Shipment(models.Model):
    """
    Shipment/İlan model - Main shipment listings
    This is the master data source (PostgreSQL)
    """
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('assigned', 'Atandı'),
        ('picked_up', 'Yük Toplandı'),
        ('in_transit', 'Yolda'),
        ('delivered', 'Teslim Edildi'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal'),
    ]

    CARGO_TYPES = [
        ('evden_eve', 'Evden Eve Nakliyat'),
        ('isyeri', 'İş Yeri Taşıma'),
        ('parcali', 'Parçalı Eşya'),
        ('arac', 'Araç Taşıma'),
        ('beyaz_esya', 'Beyaz Eşya'),
        ('mobilya', 'Mobilya'),
        ('diger', 'Diğer'),
    ]

    # Shipment identification
    shipment_id = models.CharField(max_length=128, unique=True, db_index=True, primary_key=True, help_text="Unique ID")
    tracking_number = models.CharField(max_length=50, unique=True, db_index=True, help_text="YN-2025-001234")

    # Shipper information
    shipper = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='shipments', help_text="Yük sahibi")
    shipper_email = models.EmailField()
    shipper_phone = models.CharField(max_length=20)

    # Shipment details
    title = models.CharField(max_length=255, help_text="İlan başlığı")
    description = models.TextField(help_text="İlan açıklaması")
    cargo_type = models.CharField(max_length=50, choices=CARGO_TYPES, default='diger')

    # Addresses (JSON fields)
    from_address_city = models.CharField(max_length=100)
    from_address_district = models.CharField(max_length=100)
    from_address_full = models.TextField()
    from_address_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    from_address_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Pickup address details (for home/office moving)
    from_floor = models.IntegerField(null=True, blank=True, help_text="Alış adresi kat numarası")
    from_has_elevator = models.BooleanField(null=True, blank=True, help_text="Alış adresinde normal asansör var mı?")
    from_has_freight_elevator = models.BooleanField(null=True, blank=True, help_text="Alış adresinde yük asansörü var mı?")
    from_room_count = models.CharField(max_length=10, null=True, blank=True, help_text="Alış adresi oda sayısı (2+1, 3+1, vb.)")

    to_address_city = models.CharField(max_length=100)
    to_address_district = models.CharField(max_length=100)
    to_address_full = models.TextField()
    to_address_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    to_address_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Delivery address details (for home/office moving)
    to_floor = models.IntegerField(null=True, blank=True, help_text="Teslimat adresi kat numarası")
    to_has_elevator = models.BooleanField(null=True, blank=True, help_text="Teslimat adresinde normal asansör var mı?")
    to_has_freight_elevator = models.BooleanField(null=True, blank=True, help_text="Teslimat adresinde yük asansörü var mı?")
    to_room_count = models.CharField(max_length=10, null=True, blank=True, help_text="Teslimat adresi oda sayısı (2+1, 3+1, vb.)")

    # Cargo details
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Ağırlık (kg)")

    # Dimensions
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Uzunluk (cm)")
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="En (cm)")
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Boy (cm)")

    # Loading/Unloading responsibility
    LOADING_CHOICES = [
        ('shipper', 'Yük Sahibi Yükleyecek'),
        ('carrier', 'Taşıyıcı Yükleyecek'),
        ('both', 'Birlikte Yüklenecek'),
    ]
    loading_responsibility = models.CharField(
        max_length=20,
        choices=LOADING_CHOICES,
        default='shipper',
        help_text="Yükleme sorumluluğu"
    )

    UNLOADING_CHOICES = [
        ('shipper', 'Yük Sahibi İndirecek'),
        ('carrier', 'Taşıyıcı İndirecek'),
        ('both', 'Birlikte İndirilecek'),
    ]
    unloading_responsibility = models.CharField(
        max_length=20,
        choices=UNLOADING_CHOICES,
        default='shipper',
        help_text="İndirme sorumluluğu"
    )

    # Pricing
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Önerilen fiyat (TRY)")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Kesinleşen fiyat")

    # Dates
    pickup_date = models.DateField(help_text="Teslim alma tarihi")
    delivery_date = models.DateField(null=True, blank=True, help_text="Teslimat tarihi")

    # Images
    images = models.JSONField(default=list, blank=True, help_text="Yük fotoğrafları (URL listesi)")

    # Status & Assignment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    assigned_bid_id = models.CharField(max_length=128, blank=True, help_text="Kabul edilen teklif ID")

    # Metrics
    view_count = models.IntegerField(default=0, help_text="Görüntülenme sayısı")
    bid_count = models.IntegerField(default=0, help_text="Teklif sayısı")

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "İlan"
        verbose_name_plural = "İlanlar"
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['tracking_number']),
            models.Index(fields=['from_address_city', 'to_address_city']),
        ]

    def __str__(self):
        return f"{self.tracking_number} - {self.title}"

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def get_active_bids(self):
        """Get all pending bids for this shipment"""
        return self.bids.filter(status='pending')


class Bid(models.Model):
    """
    Bid/Offer model - Carriers make bids on shipments
    This is the master data source (PostgreSQL)
    """
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
        ('withdrawn', 'Geri Çekildi'),
        ('counter_offered', 'Karşı Teklif Verildi'),
    ]

    # Bid identification
    bid_id = models.CharField(max_length=128, unique=True, db_index=True, primary_key=True, help_text="Unique ID")

    # Shipment information (ForeignKey to Shipment)
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, related_name='bids', help_text="İlan")
    tracking_number = models.CharField(max_length=50, db_index=True, help_text="İlan takip numarası")

    # Carrier (bidder) information - PostgreSQL ForeignKey
    carrier = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='carrier_bids', null=True, blank=True, help_text="Taşıyıcı profili")
    carrier_email = models.EmailField()
    carrier_name = models.CharField(max_length=255, blank=True)
    carrier_phone = models.CharField(max_length=20, blank=True)
    carrier_verified = models.BooleanField(default=False, help_text="Taşıyıcı belgeleri onaylı mı?")

    # Shipper information
    shipper_email = models.EmailField()

    # Bid details
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Teklif edilen fiyat (TRY)")
    estimated_delivery_days = models.IntegerField(default=1, help_text="Tahmini teslimat günü")
    message = models.TextField(blank=True, help_text="Taşıyıcının mesajı")

    # Counter offer (shipper can propose different price)
    counter_offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Karşı teklif fiyatı (TRY)")
    counter_offer_message = models.TextField(blank=True, help_text="Karşı teklif mesajı")
    counter_offered_at = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Teklif"
        verbose_name_plural = "Teklifler"
        indexes = [
            models.Index(fields=['shipment_id', 'status']),
            models.Index(fields=['tracking_number']),
        ]

    def __str__(self):
        return f"{self.tracking_number} - {self.carrier_email} - {self.offered_price} TL"

    def get_final_price(self):
        """Get the final negotiated price"""
        return self.counter_offer_price if self.counter_offer_price else self.offered_price


class BidComment(models.Model):
    """
    Comments on bids - Both shipper and carrier can comment
    """
    # Comment identification
    comment_id = models.AutoField(primary_key=True)

    # Related bid
    bid = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='comments', help_text="Teklif")

    # Author (can be shipper or carrier)
    author = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='bid_comments', help_text="Yorum yazarı")
    author_email = models.EmailField()
    author_name = models.CharField(max_length=255)
    is_shipper = models.BooleanField(default=False, help_text="Yük sahibi mi?")

    # Comment content
    comment = models.TextField(help_text="Yorum metni")

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Teklif Yorumu"
        verbose_name_plural = "Teklif Yorumları"
        indexes = [
            models.Index(fields=['bid', 'created_at']),
        ]

    def __str__(self):
        return f"{self.author_name} - {self.bid.bid_id} - {self.created_at}"


class Payment(models.Model):
    """
    Payment model - Tracks payments from shippers to carriers
    Admin manually transfers money after delivery confirmation
    """
    PAYMENT_STATUS = [
        ('pending', 'Ödeme Bekliyor'),           # Waiting for shipper to pay
        ('paid', 'Ödendi'),                      # Shipper paid, money held
        ('in_transit', 'Taşınıyor'),             # Carrier picked up cargo
        ('delivered', 'Teslim Edildi'),          # Both parties confirmed delivery
        ('completed', 'Tamamlandı'),             # Admin transferred money to carrier
        ('refunded', 'İade Edildi'),             # Payment refunded to shipper
        ('disputed', 'İhtilaf'),                 # Dispute between parties
    ]

    # Payment identification
    payment_id = models.CharField(max_length=128, unique=True, db_index=True, primary_key=True)

    # Related objects
    shipment = models.OneToOneField('Shipment', on_delete=models.CASCADE, related_name='payment')
    bid = models.OneToOneField('Bid', on_delete=models.CASCADE, related_name='payment')

    # Payment parties
    shipper = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='payments_made')
    carrier = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='payments_received')

    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Ödeme tutarı (TRY)")
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Platform komisyonu (TRY)")
    carrier_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Taşıyıcıya gidecek tutar (TRY)")

    # Payment status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    # Virtual POS information
    payment_method = models.CharField(max_length=50, default='credit_card', help_text="Ödeme yöntemi")
    transaction_id = models.CharField(max_length=255, blank=True, help_text="Sanal POS işlem ID")
    payment_provider = models.CharField(max_length=100, blank=True, help_text="Ödeme sağlayıcı (iyzico, paytr, vb)")

    # Delivery confirmation
    shipper_confirmed_delivery = models.BooleanField(default=False, help_text="Yük sahibi teslim onayı")
    carrier_confirmed_delivery = models.BooleanField(default=False, help_text="Taşıyıcı teslim onayı")
    shipper_confirmed_at = models.DateTimeField(null=True, blank=True)
    carrier_confirmed_at = models.DateTimeField(null=True, blank=True)

    # Admin transfer
    admin_transferred = models.BooleanField(default=False, help_text="Admin tarafından transfer edildi mi?")
    admin_transferred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferred_payments')
    admin_transferred_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Admin notları")

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True, help_text="Ödeme yapıldığı zaman")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Transfer tamamlandığı zaman")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ödeme"
        verbose_name_plural = "Ödemeler"
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['shipper', 'status']),
            models.Index(fields=['carrier', 'status']),
        ]

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.amount} TL - {self.get_status_display()}"

    def calculate_carrier_amount(self):
        """Calculate amount that goes to carrier after platform fee"""
        self.carrier_amount = self.amount - self.platform_fee
        return self.carrier_amount

    def is_delivery_confirmed(self):
        """Check if both parties confirmed delivery"""
        return self.shipper_confirmed_delivery and self.carrier_confirmed_delivery

    def can_transfer_to_carrier(self):
        """Check if payment can be transferred to carrier"""
        return (
            self.status == 'delivered' and
            self.is_delivery_confirmed() and
            not self.admin_transferred
        )


class ShipmentTracking(models.Model):
    """
    Tracking updates for shipments - Status history log
    Records each status change with timestamp and location
    """
    # Tracking ID
    tracking_id = models.AutoField(primary_key=True)

    # Related shipment
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, related_name='tracking_updates', help_text="İlan")

    # Status update
    status = models.CharField(max_length=20, help_text="Durum")
    status_display = models.CharField(max_length=100, help_text="Durum açıklaması")

    # Location
    location = models.CharField(max_length=200, blank=True, help_text="Konum (şehir/ilçe)")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Details
    note = models.TextField(blank=True, help_text="Ek notlar")

    # Who updated (carrier or system)
    updated_by = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, blank=True, help_text="Güncelleyen")
    is_automatic = models.BooleanField(default=False, help_text="Otomatik güncelleme mi?")

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Takip Kaydı"
        verbose_name_plural = "Takip Kayıtları"
        indexes = [
            models.Index(fields=['shipment', '-created_at']),
        ]

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status_display} - {self.created_at}"


class DeliveryProof(models.Model):
    """
    Delivery proof - Photos, signatures, notes at delivery
    Both shipper and carrier can upload proof
    """
    # Proof ID
    proof_id = models.AutoField(primary_key=True)

    # Related shipment
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, related_name='delivery_proofs', help_text="İlan")

    # Uploader
    uploaded_by = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='uploaded_proofs', help_text="Yükleyen")
    is_shipper = models.BooleanField(default=False, help_text="Yük sahibi mi?")

    # Proof type
    PROOF_TYPES = [
        ('photo', 'Fotoğraf'),
        ('signature', 'İmza'),
        ('document', 'Belge'),
    ]
    proof_type = models.CharField(max_length=20, choices=PROOF_TYPES, default='photo')

    # File
    file_url = models.URLField(help_text="Firebase Storage URL veya data URL")

    # Description
    description = models.TextField(blank=True, help_text="Açıklama")

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Teslimat Kanıtı"
        verbose_name_plural = "Teslimat Kanıtları"
        indexes = [
            models.Index(fields=['shipment', '-created_at']),
        ]

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.get_proof_type_display()} - {self.created_at}"


class Review(models.Model):
    """
    Reviews and ratings - Both parties rate each other after delivery
    Shipper rates carrier, carrier rates shipper
    """
    # Review ID
    review_id = models.AutoField(primary_key=True)

    # Related shipment and bid
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, related_name='reviews', help_text="İlan")
    bid = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='reviews', help_text="Teklif")

    # Reviewer and reviewed
    reviewer = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='reviews_given', help_text="Değerlendiren")
    reviewed = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='reviews_received', help_text="Değerlendirilen")

    # Rating (1-5 stars)
    rating = models.IntegerField(help_text="Puan (1-5)")

    # Rating categories
    communication_rating = models.IntegerField(default=5, help_text="İletişim puanı (1-5)")
    professionalism_rating = models.IntegerField(default=5, help_text="Profesyonellik puanı (1-5)")
    punctuality_rating = models.IntegerField(default=5, help_text="Zamanında teslimat puanı (1-5)")

    # Review content
    comment = models.TextField(blank=True, help_text="Yorum (opsiyonel)")

    # Review type
    is_shipper_review = models.BooleanField(default=False, help_text="Yük sahibinin yazdığı değerlendirme mi?")

    # Moderation
    is_visible = models.BooleanField(default=True, help_text="Görünür mü?")
    is_flagged = models.BooleanField(default=False, help_text="Şikayet edildi mi?")

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Değerlendirme"
        verbose_name_plural = "Değerlendirmeler"
        indexes = [
            models.Index(fields=['reviewed', '-created_at']),
            models.Index(fields=['shipment']),
        ]
        # Ensure one review per person per shipment
        unique_together = ['shipment', 'reviewer']

    def __str__(self):
        return f"{self.reviewer.user.email} → {self.reviewed.user.email} - {self.rating}⭐ - {self.shipment.tracking_number}"

    def save(self, *args, **kwargs):
        """Update user's average rating when review is saved"""
        super().save(*args, **kwargs)

        # Recalculate average rating for reviewed user
        reviews = Review.objects.filter(reviewed=self.reviewed, is_visible=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.reviewed.rating_avg = round(avg_rating, 2)
            self.reviewed.rating_count = reviews.count()
            self.reviewed.save(update_fields=['rating_avg', 'rating_count'])
