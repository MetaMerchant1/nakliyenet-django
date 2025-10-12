# 🚚 NAKLIYE NET - Django Web Platform

Django tabanlı SEO-optimize web sitesi. Flutter mobil uygulamaları ile aynı Firebase veritabanını paylaşır.

## 📋 Özellikler

- ✅ **SEO Optimize** - Server-side rendering ile mükemmel SEO
- ✅ **Firebase Entegrasyonu** - Flutter app ile aynı Firestore database
- ✅ **Dinamik Sitemap** - Google için otomatik sitemap oluşturma
- ✅ **Open Graph** - Sosyal medya paylaşımları için zengin kartlar
- ✅ **Schema.org** - Structured data ile rich results
- ✅ **Responsive** - Bootstrap 5 ile mobil uyumlu
- ✅ **Deep Linking** - Mobil app ile entegrasyon

## 🛠️ Kurulum

### 1. Gereksinimler

```bash
Python 3.9+
pip (Python package manager)
Firebase Admin SDK credentials
```

### 2. Sanal Ortam Oluşturma

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt
```

### 4. Firebase Credentials

1. Firebase Console'a gidin: https://console.firebase.google.com
2. Project Settings > Service Accounts
3. "Generate New Private Key" butonuna tıklayın
4. İndirilen JSON dosyasını `firebase-adminsdk.json` olarak kaydedin
5. Bu dosyayı projenin kök dizinine koyun

### 5. Ortam Değişkenlerini Ayarlama

```bash
# .env.example dosyasını .env olarak kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin
# SECRET_KEY, ALLOWED_HOSTS vb. ayarlayın
```

### 6. Django Migrate

```bash
python manage.py migrate
```

### 7. Admin Kullanıcısı Oluşturma (Opsiyonel)

```bash
python manage.py createsuperuser
```

### 8. Geliştirme Sunucusunu Başlatma

```bash
python manage.py runserver
```

Site şu adreste çalışacak: http://127.0.0.1:8000

## 📁 Proje Yapısı

```
nakliyenet_django/
├── nakliyenet/          # Django projesi
│   ├── settings.py      # Ayarlar
│   ├── urls.py          # Ana URL routing
│   └── wsgi.py          # WSGI config
├── website/             # Ana web uygulaması
│   ├── views.py         # View'ler (SEO sayfaları)
│   ├── urls.py          # URL patterns
│   ├── sitemaps.py      # Dinamik sitemap
│   └── context_processors.py
├── templates/           # HTML template'ler
│   ├── base.html        # Ana template
│   └── website/
│       ├── index.html   # Ana sayfa
│       ├── ilan_detay.html  # İlan detay (ÖNEMLİ!)
│       └── ilanlar.html # İlan listesi
├── static/              # CSS, JS, images
├── firebase_service.py  # Firebase Firestore servisleri
├── requirements.txt     # Python bağımlılıkları
├── manage.py            # Django CLI
└── README.md
```

## 🔥 Firebase Servisleri

### ShipmentService

```python
from firebase_service import shipment_service

# Aktif ilanları getir
shipments = shipment_service.get_all_active(limit=50)

# İlan numarasına göre getir
shipment = shipment_service.get_by_tracking_number('YN-2025-001234')

# Şehre göre filtrele
istanbul_shipments = shipment_service.get_by_city('İstanbul')
```

### UserService

```python
from firebase_service import user_service

# Kullanıcı bilgilerini getir
user = user_service.get_user(uid='user_id_here')
```

## 🚀 Production Deployment

### Heroku Deployment

1. **Heroku CLI Kurulumu**
   ```bash
   # https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Heroku App Oluşturma**
   ```bash
   heroku create nakliyenet-web
   ```

3. **Ortam Değişkenlerini Ayarlama**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS="nakliyenet-web.herokuapp.com,nakliyenet.com"

   # Firebase credentials (base64 encode edilmiş)
   heroku config:set FIREBASE_CREDENTIALS="$(cat firebase-adminsdk.json | base64)"
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Migration**
   ```bash
   heroku run python manage.py migrate
   ```

### Procfile (Heroku için)

```
web: gunicorn nakliyenet.wsgi --log-file -
```

### runtime.txt (Heroku için)

```
python-3.11.5
```

## 🌐 Domain Ayarları

### nakliyenet.com → Django Web

1. DNS ayarlarından A kaydı ekleyin
2. Heroku'da custom domain ekleyin:
   ```bash
   heroku domains:add nakliyenet.com
   heroku domains:add www.nakliyenet.com
   ```

3. SSL sertifikası otomatik yüklenecek

## 📱 Mobil App Entegrasyonu

### Deep Linking

Django web'den mobil app'e yönlendirme:

```html
<!-- Uygulamada Aç butonu -->
<a href="nakliyenet://shipment/YN-2025-001234">
    Uygulamada Aç
</a>

<!-- Universal Link -->
<a href="https://nakliyenet.com/ilan/YN-2025-001234/">
    İlanı Görüntüle
</a>
```

### Flutter App Değişiklikleri

Flutter app'inize deep linking ekleyin:

```yaml
# pubspec.yaml
dependencies:
  uni_links: ^0.5.1
```

## 🔍 SEO Checklist

- [x] Server-side rendering
- [x] Unique title tags (her sayfa için)
- [x] Meta descriptions (155 karakter)
- [x] Canonical URLs
- [x] Open Graph tags
- [x] Twitter Cards
- [x] Schema.org structured data
- [x] Sitemap.xml (dinamik)
- [x] robots.txt
- [x] Breadcrumbs
- [x] Semantic HTML
- [x] Alt tags (images için)
- [x] Mobile-friendly
- [x] Fast loading (whitenoise)

## 📊 Google Search Console

1. https://search.google.com/search-console
2. Property ekle: nakliyenet.com
3. Sitemap gönder: https://nakliyenet.com/sitemap.xml
4. İndexleme istekleri gönder

## 🎯 Önemli URL'ler

- **Ana Sayfa**: `/`
- **İlan Listesi**: `/ilanlar/`
- **İlan Detay**: `/ilan/YN-2025-001234/`
- **Şehir Filtresi**: `/ilanlar/?sehir=İstanbul`
- **Sitemap**: `/sitemap.xml`
- **Admin Panel**: `/admin/`

## 🐛 Debugging

### Firebase Bağlantı Hatası

```bash
# Firebase credentials kontrolü
python -c "import firebase_service; firebase_service.initialize_firebase()"
```

### Template Hatası

```bash
# Template'leri kontrol et
python manage.py check
```

### Static Files

```bash
# Static dosyaları topla
python manage.py collectstatic --noinput
```

## 📈 Performans İyileştirme

- [ ] Redis cache ekle
- [ ] CDN kullan (Cloudflare)
- [ ] Image optimization
- [ ] Lazy loading
- [ ] Minify CSS/JS

## 🔒 Güvenlik

- [ ] HTTPS zorunlu yap
- [ ] CSRF protection aktif
- [ ] XSS protection
- [ ] SQL Injection koruması (Django ORM kullanılıyor)
- [ ] Rate limiting ekle
- [ ] Security headers

## 📞 Destek

Sorularınız için: support@nakliyenet.com

## 📝 Lisans

© 2025 NAKLIYE NET. Tüm hakları saklıdır.
