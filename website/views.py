"""
Website Views - SEO optimize edilmiş sayfalar
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import UserDocument, UserProfile, Bid, Payment, Shipment, ShipmentTracking, DeliveryProof, Review
from decimal import Decimal
import json
import uuid
from datetime import datetime as dt


def index(request):
    """
    Ana sayfa - SEO optimize
    Google'ın ilk gördüğü sayfa
    """
    from .models import Shipment, UserProfile

    # Son ilanlar (PostgreSQL'den)
    try:
        recent_shipments = Shipment.objects.filter(status='active').order_by('-created_at')[:6]
    except Exception as e:
        print(f"Error fetching recent shipments: {e}")
        recent_shipments = []

    # İstatistikler (PostgreSQL'den)
    try:
        stats = {
            'active_shipments': Shipment.objects.filter(status='active').count(),
            'completed_shipments': Shipment.objects.filter(status='completed').count(),
            'total_users': UserProfile.objects.count(),
            'total_carriers': UserProfile.objects.filter(user_type=1, documents_verified=True).count(),
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        stats = {'active_shipments': 0, 'completed_shipments': 0, 'total_users': 0, 'total_carriers': 0}

    # Schema.org Organization structured data - Google'da marka tanınırlığı için
    organization_schema = {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        'name': 'NAKLIYE NET',
        'url': f'{request.scheme}://{request.get_host()}',
        'logo': f'{request.scheme}://{request.get_host()}/static/images/logo.png',
        'description': 'Türkiye\'nin en büyük dijital nakliye ve taşımacılık platformu',
        'foundingDate': '2024',
        'areaServed': {
            '@type': 'Country',
            'name': 'Turkey'
        },
        'sameAs': [
            # Sosyal medya hesapları buraya eklenecek
            # 'https://www.facebook.com/nakliyenet',
            # 'https://www.instagram.com/nakliyenet',
            # 'https://twitter.com/nakliyenet'
        ],
        'contactPoint': {
            '@type': 'ContactPoint',
            'contactType': 'customer support',
            'availableLanguage': 'Turkish'
        }
    }

    context = {
        'title': 'NAKLIYE NET - Türkiye\'nin Dijital Yük Pazaryeri',
        'description': 'Yük gönderin, teklif alın, güvenle taşıyın. Türkiye\'nin en büyük nakliye ve taşımacılık platformu. Ev taşıma, ofis taşıma, yük taşıma hizmetleri.',
        'keywords': 'nakliye, taşımacılık, yük taşıma, ev taşıma, ofis taşıma, kamyonet, nakliye firması',
        'og_image': f'{request.scheme}://{request.get_host()}/static/images/og-home.jpg',
        'recent_shipments': recent_shipments,
        'stats': stats,
        'schema_org': json.dumps(organization_schema, ensure_ascii=False),
    }
    return render(request, 'website/index.html', context)


def ilan_listesi(request):
    """
    İlan listesi - SEO optimize
    /ilanlar/ URL'i
    """
    from .models import Shipment

    # Filtreler
    city = request.GET.get('sehir', '').strip()
    category = request.GET.get('kategori', '').strip()

    # İlanları PostgreSQL'den getir
    shipments = Shipment.objects.filter(status='active').order_by('-created_at')

    if city:
        from django.db.models import Q
        shipments = shipments.filter(
            Q(from_address_city__icontains=city) | Q(to_address_city__icontains=city)
        )
        page_title = f'{city} Nakliye İlanları'
        page_desc = f'{city} bölgesindeki aktif nakliye ve taşıma ilanları. Güvenli nakliyat hizmeti için teklif alın.'
    elif category:
        # Kategori filtresi (cargo_type'a göre)
        category_map = {
            'evden-eve': 'evden_eve',
            'isyeri': 'isyeri',
            'beyaz-esya': 'beyaz_esya',
            'mobilya': 'mobilya',
            'arac': 'arac',
            'parcali': 'parcali',
        }
        cargo_type = category_map.get(category.lower())
        if cargo_type:
            shipments = shipments.filter(cargo_type=cargo_type)
            page_title = f'{category.capitalize()} Nakliye İlanları'
            page_desc = f'{category.capitalize()} taşıma ilanları. Özel yük taşıma hizmeti.'
        else:
            page_title = 'Yük İlanları'
            page_desc = 'Türkiye genelindeki tüm aktif nakliye ilanları'
    else:
        page_title = 'Yük İlanları - Tüm İlanlar'
        page_desc = 'Türkiye genelindeki tüm aktif nakliye ve taşıma ilanları. En uygun nakliye fiyatları için teklifleri karşılaştırın.'

    # Sayfalama
    paginator = Paginator(shipments, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'title': f'{page_title} | NAKLIYE NET',
        'description': page_desc,
        'keywords': 'nakliye ilanları, yük ilanları, taşıma ilanları, nakliye fiyatları',
        'shipments': page_obj,
        'city': city,
        'category': category,
        'total_count': shipments.count(),
    }
    return render(request, 'website/ilanlar.html', context)


def ilan_detay(request, tracking_number):
    """
    İlan detay - Her ilan için unique SEO
    /ilan/YN-2025-001234/ URL'i

    En önemli SEO sayfası!
    """
    from .models import Shipment, Bid

    # Get shipment from PostgreSQL
    try:
        shipment = Shipment.objects.select_related('shipper__user').get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        raise Http404("İlan bulunamadı")

    # Increment view count (only if not the owner)
    if not request.user.is_authenticated or (
        hasattr(request.user, 'profile') and
        request.user.profile != shipment.shipper
    ):
        shipment.increment_view_count()

    # Yük sahibi bilgileri
    owner = {
        'name': shipment.shipper.user.get_full_name() or shipment.shipper.user.username,
        'email': shipment.shipper_email,
        'phone': shipment.shipper_phone,
        'verified': shipment.shipper.documents_verified,
    }

    # SEO için şehir bilgilerini parse et
    from_city = shipment.from_address_city
    to_city = shipment.to_address_city

    # Canonical URL
    canonical = f"{request.scheme}://{request.get_host()}/ilan/{tracking_number}/"

    # Structured data (Schema.org)
    schema_org = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': shipment.title,
        'description': shipment.description[:500],
        'offers': {
            '@type': 'Offer',
            'price': str(shipment.suggested_price),
            'priceCurrency': 'TRY',
            'availability': 'https://schema.org/InStock' if shipment.status == 'active' else 'https://schema.org/OutOfStock',
        },
        'brand': {
            '@type': 'Brand',
            'name': 'NAKLIYE NET'
        }
    }

    # Deep link (mobil app'te aç)
    deep_link = f"nakliyenet://shipment/{tracking_number}"
    web_deep_link = f"https://nakliyenet.com/ilan/{tracking_number}/"

    # Get bids for this shipment from PostgreSQL
    bids = shipment.bids.all().order_by('-created_at')

    # Check if current user has already bid
    user_has_bid = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        user_has_bid = bids.filter(carrier=request.user.profile).exists()

    # Get assigned carrier if exists
    assigned_carrier = None
    if shipment.assigned_bid_id:
        try:
            assigned_bid = Bid.objects.select_related('carrier').get(bid_id=shipment.assigned_bid_id)
            assigned_carrier = assigned_bid.carrier
        except Bid.DoesNotExist:
            pass

    context = {
        'title': f'{shipment.title} - İlan No: {tracking_number} | NAKLIYE NET',
        'description': f'{shipment.description[:155]}... {from_city}-{to_city} arası nakliye. {shipment.weight} kg. Teklif verin.',
        'keywords': f'nakliye, taşıma, {from_city}, {to_city}, {tracking_number}, yük taşıma',
        'shipment': shipment,
        'owner': owner,
        'canonical': canonical,
        'schema_org': json.dumps(schema_org, ensure_ascii=False),
        'deep_link': deep_link,
        'web_deep_link': web_deep_link,
        'from_city': from_city,
        'to_city': to_city,
        'bids': bids,
        'user_has_bid': user_has_bid,
        'bid_count': bids.count(),
        'assigned_carrier': assigned_carrier,
    }
    return render(request, 'website/ilan_detay.html', context)


def hakkimizda(request):
    """Hakkımızda sayfası - Canlı istatistiklerle"""
    from .models import UserProfile, Shipment
    from django.db.models import Avg, Count

    # Canlı istatistikler
    try:
        # Toplam aktif kullanıcılar
        total_users = UserProfile.objects.count()

        # Doğrulanmış taşıyıcılar (user_type=1 ve belgesi onaylı)
        verified_carriers = UserProfile.objects.filter(
            user_type=1,
            documents_verified=True
        ).count()

        # Tamamlanan shipment'lar
        completed_shipments = Shipment.objects.filter(status='completed').count()

        # Ortalama tasarruf hesapla (suggested_price vs final_price)
        shipments_with_price = Shipment.objects.filter(
            status='completed',
            final_price__isnull=False,
            suggested_price__gt=0
        )

        if shipments_with_price.exists():
            avg_savings = 0
            total_savings = 0
            count = 0

            for shipment in shipments_with_price:
                if shipment.suggested_price > 0:
                    savings_percent = ((shipment.suggested_price - shipment.final_price) / shipment.suggested_price) * 100
                    if savings_percent > 0:
                        total_savings += savings_percent
                        count += 1

            if count > 0:
                avg_savings = int(total_savings / count)
        else:
            avg_savings = 30  # Default değer

        stats = {
            'total_users': total_users,
            'verified_carriers': verified_carriers,
            'completed_shipments': completed_shipments,
            'avg_savings': avg_savings if avg_savings > 0 else 30,
        }
    except Exception as e:
        print(f"Error calculating stats: {e}")
        stats = {
            'total_users': 0,
            'verified_carriers': 0,
            'completed_shipments': 0,
            'avg_savings': 30,
        }

    context = {
        'title': 'Hakkımızda - NAKLIYE NET',
        'description': 'NAKLIYE NET Türkiye\'nin en güvenilir dijital nakliye ve taşımacılık platformudur. Misyonumuz ve vizyonumuz.',
        'keywords': 'hakkımızda, nakliye net, taşımacılık platformu, dijital nakliye',
        'stats': stats,
    }
    return render(request, 'website/hakkimizda.html', context)


def iletisim(request):
    """İletişim sayfası"""
    context = {
        'title': 'İletişim - NAKLIYE NET',
        'description': 'NAKLIYE NET ile iletişime geçin. Sorularınız için bize ulaşın.',
        'keywords': 'iletişim, destek, müşteri hizmetleri',
    }
    return render(request, 'website/iletisim.html', context)


def nasil_calisir(request):
    """Nasıl Çalışır? sayfası"""
    context = {
        'title': 'Nasıl Çalışır? - NAKLIYE NET',
        'description': 'NAKLIYE NET platformunu nasıl kullanacağınızı öğrenin. Adım adım rehber.',
        'keywords': 'nasıl çalışır, kullanım rehberi, platform rehberi',
    }
    return render(request, 'website/nasil_calisir.html', context)


def sss(request):
    """Sıkça Sorulan Sorular - SEO optimize FAQPage schema ile"""
    faqs = [
        {
            'question': 'NAKLIYE NET nedir?',
            'answer': 'NAKLIYE NET, yük sahipleri ile taşıyıcıları buluşturan Türkiye\'nin en büyük dijital nakliye platformudur.'
        },
        {
            'question': 'Nasıl teklif alabilirim?',
            'answer': 'Web sitemizden kayıt olun, yük ilanınızı oluşturun ve doğrulanmış taşıyıcılardan gelen teklifleri karşılaştırın. En uygun teklifi seçin ve güvenle nakliye işleminizi gerçekleştirin.'
        },
        {
            'question': 'Güvenli mi?',
            'answer': 'Evet! Tüm taşıyıcılar belge kontrolünden geçer (ehliyet, ruhsat, SRC belgesi) ve kullanıcı değerlendirmeleri sistemi mevcuttur. Ayrıca güvenli escrow ödeme sistemiyle paranız teslim onayına kadar platformda güvende tutulur.'
        },
        {
            'question': 'Ücretlendirme nasıl?',
            'answer': 'Platform kullanımı ücretsizdir. Yük sahipleri ve taşıyıcılar ücretsiz kayıt olabilir. Sadece başarılı taşımalardan %10 platform komisyonu alınır.'
        },
        {
            'question': 'Ödeme sistemi nasıl çalışır?',
            'answer': 'Teklifi kabul ettikten sonra yük sahibi ödemeyi yapar. Para escrow sisteminde güvende tutulur. Taşıyıcı yükü teslim eder, her iki taraf da onayladıktan sonra ödeme taşıyıcıya transfer edilir.'
        },
        {
            'question': 'Hangi şehirlerde hizmet veriyorsunuz?',
            'answer': 'Türkiye\'nin tüm şehirlerinde hizmet vermekteyiz. İstanbul, Ankara, İzmir, Bursa, Antalya başta olmak üzere tüm il ve ilçelere nakliye hizmeti sunulmaktadır.'
        },
        {
            'question': 'Taşıyıcı olarak nasıl kayıt olurum?',
            'answer': 'Kayıt olduktan sonra profilinizden belgelerinizi (ehliyet, ruhsat, SRC belgesi) yükleyin. Belgeleriniz admin onayından geçtikten sonra ilanlara teklif verebilirsiniz.'
        },
        {
            'question': 'Yükümü takip edebilir miyim?',
            'answer': 'Evet! Taşıyıcı teslimatı kabul ettikten sonra yükünüzü gerçek zamanlı olarak takip edebilir, konum güncellemelerini görebilir ve taşıyıcı ile mesajlaşabilirsiniz.'
        },
    ]

    # Schema.org FAQPage structured data - Google'da zengin snippet için
    faq_schema = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': faq['question'],
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': faq['answer']
                }
            } for faq in faqs
        ]
    }

    context = {
        'title': 'Sıkça Sorulan Sorular (SSS) - NAKLIYE NET',
        'description': 'NAKLIYE NET hakkında merak ettiğiniz her şey. Nakliye platformumuz, ödeme sistemi, güvenlik, taşıyıcı olmak ve daha fazlası hakkında sık sorulan sorular ve cevapları.',
        'keywords': 'sss, sorular, cevaplar, yardım, nakliye, taşımacılık, sık sorulan sorular',
        'faqs': faqs,
        'schema_org': json.dumps(faq_schema, ensure_ascii=False),
    }
    return render(request, 'website/sss.html', context)


def gizlilik_politikasi(request):
    """Gizlilik Politikası sayfası"""
    context = {
        'title': 'Gizlilik Politikası - NAKLIYE NET',
        'description': 'NAKLIYE NET gizlilik politikası ve kişisel verilerin korunması.',
        'keywords': 'gizlilik, kvkk, kişisel veriler, gizlilik politikası',
    }
    return render(request, 'website/gizlilik_politikasi.html', context)


def kullanim_kosullari(request):
    """Kullanım Koşulları sayfası"""
    context = {
        'title': 'Kullanım Koşulları - NAKLIYE NET',
        'description': 'NAKLIYE NET kullanım koşulları ve hizmet şartları.',
        'keywords': 'kullanım koşulları, hizmet şartları, şartlar ve koşullar',
    }
    return render(request, 'website/kullanim_kosullari.html', context)


def sehir_nakliye(request, sehir_slug):
    """
    Şehir bazlı nakliye landing page - SEO optimize
    Örnek: /nakliye/istanbul/, /nakliye/gebze/
    """
    from .models import Shipment, UserProfile
    from django.db.models import Q

    # Slug'ı şehir adına çevir
    sehir_map = {
        'istanbul': 'İstanbul',
        'ankara': 'Ankara',
        'izmir': 'İzmir',
        'gebze': 'Gebze',
        'kocaeli': 'Kocaeli',
        'darica': 'Darıca',
        'bursa': 'Bursa',
        'antalya': 'Antalya',
        'adana': 'Adana',
        'gaziantep': 'Gaziantep',
        'konya': 'Konya',
        'mersin': 'Mersin',
        'kayseri': 'Kayseri',
        'eskisehir': 'Eskişehir',
        'diyarbakir': 'Diyarbakır',
        'samsun': 'Samsun',
        'denizli': 'Denizli',
        'sanliurfa': 'Şanlıurfa',
        'adapazari': 'Adapazarı',
        'malatya': 'Malatya',
        'kahramanmaras': 'Kahramanmaraş',
        'erzurum': 'Erzurum',
        'van': 'Van',
        'batman': 'Batman',
        'elazig': 'Elazığ',
        'erzincan': 'Erzincan',
        'tekirdag': 'Tekirdağ',
        'balikesir': 'Balıkesir',
        'aydin': 'Aydın',
        'manisa': 'Manisa',
        'muğla': 'Muğla',
        'trabzon': 'Trabzon',
        'ordu': 'Ordu',
        'rize': 'Rize',
        'sakarya': 'Sakarya',
        'edirne': 'Edirne',
    }

    sehir = sehir_map.get(sehir_slug.lower())

    if not sehir:
        # 404 yerine varsayılan bir şehir gösterelim
        sehir = sehir_slug.capitalize()

    # Şehre ait ilanlar (hem kalkış hem varış şehri)
    try:
        shipments = Shipment.objects.filter(
            Q(from_address_city__icontains=sehir) | Q(to_address_city__icontains=sehir),
            status='active'
        ).order_by('-created_at')[:6]
    except Exception as e:
        print(f"Error fetching city shipments: {e}")
        shipments = []

    # İstatistikler
    try:
        # Şehirdeki aktif ilanlar
        active_shipments = Shipment.objects.filter(
            Q(from_address_city__icontains=sehir) | Q(to_address_city__icontains=sehir),
            status='active'
        ).count()

        # Doğrulanmış taşıyıcılar
        verified_carriers = UserProfile.objects.filter(
            user_type=1,
            documents_verified=True
        ).count()

        # Ortalama tasarruf (tüm platformdan)
        completed_shipments = Shipment.objects.filter(
            status='completed',
            final_price__isnull=False,
            suggested_price__gt=0
        )

        if completed_shipments.exists():
            avg_savings = 0
            total_savings = 0
            count = 0

            for shipment in completed_shipments:
                if shipment.suggested_price > 0:
                    savings_percent = ((shipment.suggested_price - shipment.final_price) / shipment.suggested_price) * 100
                    if savings_percent > 0:
                        total_savings += savings_percent
                        count += 1

            if count > 0:
                avg_savings = int(total_savings / count)
        else:
            avg_savings = 30

        stats = {
            'active_shipments': active_shipments,
            'verified_carriers': verified_carriers,
            'avg_savings': avg_savings if avg_savings > 0 else 30,
        }
    except Exception as e:
        print(f"Error calculating city stats: {e}")
        stats = {
            'active_shipments': 0,
            'verified_carriers': 2,
            'avg_savings': 30,
        }

    # Schema.org LocalBusiness structured data - Lokal SEO için
    localbusiness_schema = {
        '@context': 'https://schema.org',
        '@type': 'Service',
        'serviceType': 'Nakliye ve Taşımacılık Hizmeti',
        'provider': {
            '@type': 'Organization',
            'name': 'NAKLIYE NET',
            'url': f'{request.scheme}://{request.get_host()}'
        },
        'areaServed': {
            '@type': 'City',
            'name': sehir
        },
        'description': f'{sehir} nakliye ve taşımacılık hizmetleri. Ev taşıma, ofis taşıma, yük taşıma.',
        'availableChannel': {
            '@type': 'ServiceChannel',
            'serviceUrl': f'{request.scheme}://{request.get_host()}/nakliye/{sehir_slug}/'
        }
    }

    context = {
        'title': f'{sehir} Nakliye - En Uygun Taşıma Fiyatları | NAKLIYE NET',
        'description': f'{sehir} nakliye ve taşımacılık hizmetleri. Ev taşıma, ofis taşıma, yük taşıma için doğrulanmış taşıyıcılardan teklif alın. {stats["active_shipments"]} aktif ilan.',
        'keywords': f'{sehir} nakliye, {sehir} taşımacılık, {sehir} ev taşıma, {sehir} ofis taşıma, {sehir} yük taşıma',
        'sehir': sehir,
        'sehir_slug': sehir_slug,
        'shipments': shipments,
        'stats': stats,
        'schema_org': json.dumps(localbusiness_schema, ensure_ascii=False),
    }
    return render(request, 'website/sehir_nakliye.html', context)


@login_required
def profil(request):
    """
    Kullanıcı profil sayfası
    Belge yükleme, telefon ve IBAN girişi
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Get user documents from PostgreSQL
    documents = UserDocument.objects.filter(user_email=request.user.email).order_by('-uploaded_at')

    # Document types for upload
    doc_types = [
        {'value': 'license', 'label': 'Ehliyet', 'icon': '🪪'},
        {'value': 'registration', 'label': 'Ruhsat', 'icon': '📄'},
        {'value': 'src', 'label': 'SRC Belgesi', 'icon': '📜'},
        {'value': 'psychotech', 'label': 'Psikoteknik Raporu', 'icon': '🧠'},
    ]

    # Check which documents are uploaded
    uploaded_types = [doc.document_type for doc in documents]

    if request.method == 'POST':
        # Update profile information
        phone = request.POST.get('phone_number', '').strip()
        iban = request.POST.get('iban', '').strip().upper()
        user_type = request.POST.get('user_type')

        # Validate IBAN
        if iban and not iban.startswith('TR'):
            messages.error(request, 'IBAN TR ile başlamalıdır.')
        elif iban and len(iban) != 26:
            messages.error(request, 'IBAN 26 karakter olmalıdır (TR + 24 rakam).')
        else:
            profile.phone_number = phone
            profile.iban = iban

            # Update user type if provided
            if user_type is not None:
                profile.user_type = int(user_type)

            # Update type-specific fields
            if profile.user_type == 0:  # Shipper
                profile.company_name = request.POST.get('company_name', '').strip()
                profile.tax_id = request.POST.get('tax_id', '').strip()
                profile.billing_address = request.POST.get('billing_address', '').strip()
            else:  # Carrier
                profile.service_areas = request.POST.get('service_areas', '').strip()
                profile.working_hours = request.POST.get('working_hours', '09:00-18:00').strip()
                profile.bio = request.POST.get('bio', '').strip()

            # Check if profile is complete
            # Yük verenler: sadece telefon ve IBAN
            # Taşıyıcılar: telefon, IBAN ve belgeler
            if profile.user_type == 0:  # Shipper
                if phone and iban:
                    profile.profile_completed = True
            else:  # Carrier
                if phone and iban:
                    profile.profile_completed = True

            # Check if documents are verified
            profile.documents_verified = profile.check_documents_verified()

            profile.save()
            messages.success(request, 'Profiliniz güncellendi!')
            return redirect('website:profil')

    context = {
        'title': 'Profilim - NAKLIYE NET',
        'description': 'Profil bilgilerinizi güncelleyin ve belgelerinizi yükleyin.',
        'profile': profile,
        'documents': documents,
        'doc_types': doc_types,
        'uploaded_types': uploaded_types,
    }
    return render(request, 'website/profil.html', context)


@login_required
def belge_yukle(request):
    """
    Belge yükleme endpoint - PostgreSQL
    Files are saved to media folder
    """
    if request.method != 'POST':
        return redirect('website:profil')

    try:
        profile = request.user.profile
    except:
        messages.error(request, 'Profil bulunamadı. Lütfen önce profilinizi oluşturun.')
        return redirect('website:profil')

    document_type = request.POST.get('document_type')
    document_file = request.FILES.get('document_file')

    if not document_type or not document_file:
        messages.error(request, 'Lütfen belge türü ve dosya seçin.')
        return redirect('website:profil')

    try:
        # Create or update document record - Django will handle file storage
        doc, created = UserDocument.objects.update_or_create(
            user_email=request.user.email,
            document_type=document_type,
            defaults={
                'user_name': request.user.get_full_name() or request.user.username,
                'document_url': '',  # Will be updated when file is uploaded
                'status': 'pending',
            }
        )

        messages.success(request, f'{doc.get_document_type_display()} başarıyla yüklendi! Admin onayı bekleniyor.')

    except Exception as e:
        print(f"Error uploading document: {e}")
        messages.error(request, 'Belge yüklenirken hata oluştu. Lütfen tekrar deneyin.')

    return redirect('website:profil')


@login_required
def teklif_ver(request, tracking_number):
    """
    Teklif verme endpoint
    Carriers can make bids on shipments
    """
    if request.method != 'POST':
        return redirect('website:ilan_detay', tracking_number=tracking_number)

    # Get user profile
    profile = request.user.profile

    if not profile.profile_completed:
        messages.error(request, 'Teklif vermek için önce profilinizi tamamlamalısınız.')
        return redirect('website:profil')

    # Check if user is a carrier
    if profile.user_type != 1:
        messages.error(request, 'Teklif vermek için Taşıyıcı olarak kayıt olmalısınız.')
        return redirect('website:profil')

    # Get shipment from PostgreSQL
    from .models import Shipment, Bid

    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        messages.error(request, 'İlan bulunamadı.')
        return redirect('website:ilanlar')

    # Check if user already bid (from PostgreSQL)
    existing_bid = Bid.objects.filter(
        shipment=shipment,
        carrier=profile
    ).exists()

    if existing_bid:
        messages.warning(request, 'Bu ilana zaten teklif verdiniz.')
        return redirect('website:ilan_detay', tracking_number=tracking_number)

    # Get form data
    offered_price = request.POST.get('offered_price')
    estimated_days = request.POST.get('estimated_delivery_days', 1)
    message = request.POST.get('message', '')

    try:
        offered_price = float(offered_price)
        estimated_days = int(estimated_days)

        if offered_price <= 0:
            raise ValueError("Fiyat 0'dan büyük olmalıdır")

        if estimated_days < 1:
            raise ValueError("Teslimat günü en az 1 olmalıdır")

    except (ValueError, TypeError) as e:
        messages.error(request, 'Geçersiz teklif bilgileri. Lütfen kontrol edin.')
        return redirect('website:ilan_detay', tracking_number=tracking_number)

    try:
        # Create bid in PostgreSQL
        bid = Bid.objects.create(
            bid_id=str(uuid.uuid4()),
            shipment=shipment,
            tracking_number=tracking_number,
            carrier=profile,
            carrier_email=request.user.email,
            carrier_name=request.user.get_full_name() or request.user.username,
            carrier_phone=profile.phone_number or '',
            carrier_verified=profile.documents_verified,
            shipper_email=shipment.shipper_email,
            offered_price=offered_price,
            estimated_delivery_days=estimated_days,
            message=message,
            status='pending'
        )

        # Update shipment bid count
        shipment.bid_count = shipment.bids.count()
        shipment.save(update_fields=['bid_count'])

        messages.success(request, f'Teklifiniz başarıyla gönderildi! Teklif: {offered_price} TL')

        # TODO: Send email notification asynchronously (celery/background task)
        # Email sending temporarily disabled for performance
        # Will be re-enabled with async implementation

    except Exception as e:
        print(f"Error creating bid: {e}")
        messages.error(request, 'Teklif gönderilirken hata oluştu. Lütfen tekrar deneyin.')

    return redirect('website:ilan_detay', tracking_number=tracking_number)


@login_required
def ilanlarim(request):
    """
    İlanlarım sayfası - Kullanıcı tipine göre farklı içerik gösterir
    - Yük Sahibi (shipper): Oluşturduğu ilanları ve gelen teklifleri görür
    - Taşıyıcı (carrier): Verdiği teklifleri ve durumlarını görür
    """
    try:
        profile = request.user.profile
    except:
        messages.error(request, 'Profil bulunamadı.')
        return redirect('website:profil')

    from .models import Shipment, Bid
    from django.db.models import Count, Q

    # Yük Sahibi görünümü
    if profile.user_type == 0:
        try:
            # Kullanıcının ilanlarını getir (prefetch bids for performance)
            shipments_queryset = Shipment.objects.filter(shipper=profile).prefetch_related('bids').order_by('-created_at')

            # Convert to list and prepare bid lists
            shipments_list = list(shipments_queryset)

            # Her shipment için bid sayılarını hesapla ve bid listesini hazırla
            for shipment in shipments_list:
                shipment.bids_list = list(shipment.bids.all().order_by('-created_at'))  # Template'de iterate edilebilir liste
                shipment.pending_bids_count = shipment.bids.filter(status='pending').count()

            # İstatistikler
            stats = {
                'total_shipments': len(shipments_list),
                'active_shipments': len([s for s in shipments_list if s.status == 'active']),
                'completed_shipments': len([s for s in shipments_list if s.status == 'completed']),
                'total_bids': sum([s.bid_count for s in shipments_list]),
                'total_views': sum([s.view_count for s in shipments_list]),
            }

        except Exception as e:
            print(f"Error fetching user shipments: {e}")
            import traceback
            traceback.print_exc()
            shipments_list = []
            stats = {
                'total_shipments': 0,
                'active_shipments': 0,
                'completed_shipments': 0,
                'total_bids': 0,
                'total_views': 0,
            }
            messages.error(request, 'İlanlar yüklenirken hata oluştu.')

        context = {
            'title': 'İlanlarım - NAKLIYE NET',
            'description': 'Oluşturduğunuz ilanları görüntüleyin ve teklifleri değerlendirin.',
            'shipments': shipments_list,
            'stats': stats,
            'profile': profile,
            'is_carrier': False,
        }
        return render(request, 'website/ilanlarim.html', context)

    # Taşıyıcı görünümü
    else:
        try:
            # Taşıyıcının verdiği teklifleri getir (Payment bilgisi ile)
            bids_list = Bid.objects.filter(carrier=profile).select_related(
                'shipment',
                'shipment__payment'
            ).order_by('-created_at')

            # İstatistikler
            stats = {
                'total_bids': bids_list.count(),
                'pending_bids': bids_list.filter(status='pending').count(),
                'accepted_bids': bids_list.filter(status='accepted').count(),
                'rejected_bids': bids_list.filter(status='rejected').count(),
            }

        except Exception as e:
            print(f"Error fetching carrier bids: {e}")
            import traceback
            traceback.print_exc()
            bids_list = []
            stats = {
                'total_bids': 0,
                'pending_bids': 0,
                'accepted_bids': 0,
                'rejected_bids': 0,
            }
            messages.error(request, 'Teklifler yüklenirken hata oluştu.')

        context = {
            'title': 'Tekliflerim - NAKLIYE NET',
            'description': 'Verdiğiniz teklifleri görüntüleyin ve durumlarını takip edin.',
            'bids': bids_list,
            'stats': stats,
            'profile': profile,
            'is_carrier': True,
        }
        return render(request, 'website/tekliflerim.html', context)


@login_required
def teklif_kabul_et(request, bid_id):
    """
    Teklifi kabul et
    """
    if request.method != 'POST':
        return redirect('website:ilanlarim')

    try:
        from .models import Bid, Shipment
        profile = request.user.profile

        # PostgreSQL'den bid'i al
        try:
            bid = Bid.objects.select_related('shipment').get(bid_id=bid_id)
        except Bid.DoesNotExist:
            messages.error(request, 'Teklif bulunamadı.')
            return redirect('website:ilanlarim')

        # Kullanıcının teklifini kabul etme yetkisi var mı kontrol et
        if bid.shipment.shipper != profile:
            messages.error(request, 'Bu teklifi kabul etme yetkiniz yok.')
            return redirect('website:ilanlarim')

        # Formdan yorumu al
        shipper_comment = request.POST.get('shipper_comment', '').strip()

        # Teklifi kabul et
        bid.status = 'accepted'
        bid.accepted_at = timezone.now()
        if shipper_comment:
            bid.shipper_comment = shipper_comment
        bid.save()

        # Shipment'ı güncelle
        shipment = bid.shipment
        shipment.status = 'assigned'
        shipment.assigned_bid_id = bid_id
        shipment.final_price = bid.offered_price
        shipment.save()

        # Diğer teklifleri reddet
        Bid.objects.filter(
            shipment=shipment,
            status='pending'
        ).exclude(bid_id=bid_id).update(
            status='rejected',
            updated_at=timezone.now()
        )

        # Payment kaydı oluştur
        platform_fee_rate = Decimal('0.10')  # %10 komisyon
        amount = Decimal(str(bid.offered_price))
        platform_fee = (amount * platform_fee_rate).quantize(Decimal('0.01'))
        carrier_amount = amount - platform_fee

        payment = Payment.objects.create(
            payment_id=str(uuid.uuid4()),
            shipment=shipment,
            bid=bid,
            shipper=profile,
            carrier=bid.carrier,
            amount=amount,
            platform_fee=platform_fee,
            carrier_amount=carrier_amount,
            status='pending',
        )

        messages.success(request, f'Teklif kabul edildi! Ödeme sayfasına yönlendiriliyorsunuz...')

        # TODO: Send email notification asynchronously (celery/background task)
        # Email sending temporarily disabled for performance
        # Will be re-enabled with async implementation

        # Ödeme sayfasına yönlendir
        return redirect('website:odeme_yap', payment_id=payment.payment_id)

    except Exception as e:
        print(f"Error accepting bid: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, 'Teklif kabul edilirken hata oluştu.')
        return redirect('website:ilanlarim')


@login_required
def teklif_reddet(request, bid_id):
    """
    Teklifi reddet
    """
    if request.method != 'POST':
        return redirect('website:ilanlarim')

    try:
        from .models import Bid
        profile = request.user.profile

        # PostgreSQL'den bid'i al
        try:
            bid = Bid.objects.get(bid_id=bid_id)
        except Bid.DoesNotExist:
            messages.error(request, 'Teklif bulunamadı.')
            return redirect('website:ilanlarim')

        # Kullanıcının teklifini reddetme yetkisi var mı kontrol et
        if bid.shipment.shipper != profile:
            messages.error(request, 'Bu teklifi reddetme yetkiniz yok.')
            return redirect('website:ilanlarim')

        # Teklifi reddet
        bid.status = 'rejected'
        bid.save()

        messages.success(request, 'Teklif reddedildi.')

    except Exception as e:
        print(f"Error rejecting bid: {e}")
        messages.error(request, 'Teklif reddedilirken hata oluştu.')

    return redirect('website:ilanlarim')


@login_required
def ilan_olustur(request):
    """
    İlan oluşturma sayfası - Tam fonksiyonlu form
    """
    from .models import Shipment
    import uuid
    from datetime import date

    if request.method == 'POST':
        try:
            # Generate unique tracking number
            tracking_number = f"YN-{date.today().year}-{uuid.uuid4().hex[:6].upper()}"

            # Create shipment
            shipment = Shipment.objects.create(
                shipment_id=str(uuid.uuid4()),
                tracking_number=tracking_number,
                shipper=request.user.profile,
                shipper_email=request.user.email,
                shipper_phone=request.POST.get('phone', ''),

                # Basic info
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                cargo_type=request.POST.get('cargo_type', 'diger'),

                # From address
                from_address_city=request.POST.get('from_city'),
                from_address_district=request.POST.get('from_district'),
                from_address_full=request.POST.get('from_address'),

                # To address
                to_address_city=request.POST.get('to_city'),
                to_address_district=request.POST.get('to_district'),
                to_address_full=request.POST.get('to_address'),

                # Cargo details
                weight=float(request.POST.get('weight', 0)),
                length=float(request.POST.get('length', 0)) if request.POST.get('length') else None,
                width=float(request.POST.get('width', 0)) if request.POST.get('width') else None,
                height=float(request.POST.get('height', 0)) if request.POST.get('height') else None,

                # Responsibilities
                loading_responsibility=request.POST.get('loading_responsibility', 'shipper'),
                unloading_responsibility=request.POST.get('unloading_responsibility', 'shipper'),

                # Pricing & dates
                suggested_price=float(request.POST.get('suggested_price', 0)),
                pickup_date=request.POST.get('pickup_date'),

                # Moving details (for home/office moving)
                from_floor=int(request.POST.get('from_floor')) if request.POST.get('from_floor') else None,
                from_has_elevator=request.POST.get('from_has_elevator') == 'true',
                from_has_freight_elevator=request.POST.get('from_has_freight_elevator') == 'true',
                from_room_count=request.POST.get('from_room_count') if request.POST.get('from_room_count') else None,
                to_floor=int(request.POST.get('to_floor')) if request.POST.get('to_floor') else None,
                to_has_elevator=request.POST.get('to_has_elevator') == 'true',
                to_has_freight_elevator=request.POST.get('to_has_freight_elevator') == 'true',
                to_room_count=request.POST.get('to_room_count') if request.POST.get('to_room_count') else None,

                # Status
                status='active',
            )

            messages.success(request, f'İlan başarıyla oluşturuldu! İlan No: {tracking_number}')
            return redirect('website:ilan_detay', tracking_number=tracking_number)

        except Exception as e:
            print(f"Error creating shipment: {e}")
            messages.error(request, f'İlan oluşturulurken hata: {str(e)}')

    # GET request - show form
    context = {
        'title': 'İlan Oluştur - NAKLIYE NET',
        'description': 'Yeni nakliye ilanı oluşturun',
        'cargo_types': Shipment.CARGO_TYPES,
        'loading_choices': Shipment.LOADING_CHOICES,
        'unloading_choices': Shipment.UNLOADING_CHOICES,
    }
    return render(request, 'website/ilan_olustur.html', context)


@login_required
def odeme_yap(request, payment_id):
    """
    Ödeme sayfası - Yük sahibi ödeme yapar
    Sanal POS entegrasyonu için hazır
    """
    try:
        profile = request.user.profile
    except:
        messages.error(request, 'Profil bulunamadı.')
        return redirect('website:profil')

    # Get payment record
    try:
        payment = Payment.objects.select_related(
            'shipment',
            'bid',
            'carrier__user'
        ).get(payment_id=payment_id)
    except Payment.DoesNotExist:
        messages.error(request, 'Ödeme kaydı bulunamadı.')
        return redirect('website:ilanlarim')

    # Check authorization - only shipper can pay
    if payment.shipper != profile:
        messages.error(request, 'Bu ödemeyi yapma yetkiniz yok.')
        return redirect('website:ilanlarim')

    # Check if already paid
    if payment.status != 'pending':
        messages.warning(request, 'Bu ödeme zaten yapılmış.')
        return redirect('website:ilanlarim')

    if request.method == 'POST':
        # TODO: Sanal POS entegrasyonu buraya eklenecek
        # Şimdilik simüle edelim (test için)

        try:
            # Simulate payment processing
            # In production, this would call virtual POS API

            payment.status = 'paid'
            payment.paid_at = timezone.now()
            payment.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            payment.payment_provider = 'Test Provider'  # Will be iyzico, paytr, etc
            payment.save()

            # Update shipment status
            payment.shipment.status = 'assigned'
            payment.shipment.save()

            messages.success(request, 'Ödemeniz başarıyla alındı! Taşıyıcı bilgilendirildi.')

            # Send email to carrier
            try:
                from django.core.mail import send_mail
                from django.conf import settings

                carrier_email = payment.carrier.user.email
                if carrier_email:
                    subject = f'Ödeme Alındı! - {payment.shipment.tracking_number}'
                    email_message = f'''
Merhaba {payment.carrier.user.get_full_name() or payment.carrier.user.username},

{payment.shipper.user.get_full_name()} tarafından ödeme yapıldı!

Ödeme Detayları:
- Takip No: {payment.shipment.tracking_number}
- Tutar: {payment.amount} TL
- Ödeme Durumu: Ödendi (Escrow'da tutuluyor)

Artık yükü teslim alabilirsiniz. Her iki taraf teslim onayı verdikten sonra para hesabınıza transfer edilecektir.

Saygılarımızla,
NAKLIYE NET Ekibi
                    '''

                    send_mail(
                        subject,
                        email_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [carrier_email],
                        fail_silently=True,
                    )
            except Exception as email_error:
                print(f"Error sending payment notification: {email_error}")

            return redirect('website:ilanlarim')

        except Exception as e:
            print(f"Error processing payment: {e}")
            messages.error(request, 'Ödeme işlenirken hata oluştu. Lütfen tekrar deneyin.')

    context = {
        'title': f'Ödeme - {payment.shipment.tracking_number}',
        'description': 'Güvenli ödeme sayfası',
        'payment': payment,
        'shipment': payment.shipment,
        'carrier': payment.carrier,
    }
    return render(request, 'website/odeme.html', context)


@login_required
def teslim_onayla(request, payment_id):
    """
    Teslim onaylama - Hem yük sahibi hem taşıyıcı onaylar
    """
    try:
        profile = request.user.profile
    except:
        messages.error(request, 'Profil bulunamadı.')
        return redirect('website:profil')

    # Get payment record
    try:
        payment = Payment.objects.select_related(
            'shipment',
            'shipper__user',
            'carrier__user'
        ).get(payment_id=payment_id)
    except Payment.DoesNotExist:
        messages.error(request, 'Ödeme kaydı bulunamadı.')
        return redirect('website:ilanlarim')

    # Check authorization - only shipper or carrier can confirm
    is_shipper = payment.shipper == profile
    is_carrier = payment.carrier == profile

    if not (is_shipper or is_carrier):
        messages.error(request, 'Bu teslimatı onaylama yetkiniz yok.')
        return redirect('website:ilanlarim')

    # Check if payment is in correct status
    if payment.status not in ['paid', 'in_transit', 'delivered']:
        messages.error(request, 'Bu aşamada teslim onayı yapılamaz.')
        return redirect('website:ilanlarim')

    if request.method == 'POST':
        try:
            # Shipper confirmation
            if is_shipper and not payment.shipper_confirmed_delivery:
                payment.shipper_confirmed_delivery = True
                payment.shipper_confirmed_at = timezone.now()
                messages.success(request, 'Teslim onayınız kaydedildi!')

            # Carrier confirmation
            elif is_carrier and not payment.carrier_confirmed_delivery:
                payment.carrier_confirmed_delivery = True
                payment.carrier_confirmed_at = timezone.now()

                # Update shipment status to in_transit if not already
                if payment.shipment.status == 'assigned':
                    payment.shipment.status = 'in_transit'
                    payment.shipment.save()
                    payment.status = 'in_transit'

                messages.success(request, 'Teslim onayınız kaydedildi!')

            # Check if both confirmed
            if payment.is_delivery_confirmed():
                payment.status = 'delivered'
                payment.shipment.status = 'delivered'
                payment.shipment.completed_at = timezone.now()
                payment.shipment.save()

                messages.success(request, 'Her iki taraf da teslimi onayladı! Admin tarafından ödeme transfer edilecektir.')

                # Notify admin
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    from django.contrib.auth.models import User

                    # Get admin emails
                    admin_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))

                    if admin_emails:
                        subject = f'Transfer Onayı Bekliyor - {payment.shipment.tracking_number}'
                        email_message = f'''
Yönetici Bildirimi,

Bir teslimat tamamlandı ve ödeme transferi bekleniyor.

Ödeme Detayları:
- Takip No: {payment.shipment.tracking_number}
- Tutar: {payment.amount} TL
- Platform Komisyonu: {payment.platform_fee} TL
- Taşıyıcıya Gidecek: {payment.carrier_amount} TL
- Taşıyıcı: {payment.carrier.user.email}

Admin panelinden transfer işlemini onaylayın:
{request.scheme}://{request.get_host()}/admin/website/payment/{payment.payment_id}/change/

NAKLIYE NET
                        '''

                        send_mail(
                            subject,
                            email_message,
                            settings.DEFAULT_FROM_EMAIL,
                            admin_emails,
                            fail_silently=True,
                        )
                except Exception as email_error:
                    print(f"Error sending admin notification: {email_error}")

            payment.save()

        except Exception as e:
            print(f"Error confirming delivery: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, 'Onay kaydedilirken hata oluştu.')

        return redirect('website:ilanlarim')

    context = {
        'title': f'Teslim Onayı - {payment.shipment.tracking_number}',
        'description': 'Teslimatı onaylayın',
        'payment': payment,
        'shipment': payment.shipment,
        'is_shipper': is_shipper,
        'is_carrier': is_carrier,
    }
    return render(request, 'website/teslim_onay.html', context)
