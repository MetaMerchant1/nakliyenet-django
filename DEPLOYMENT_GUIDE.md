# 🚀 DEPLOYMENT GUIDE - NAKLIYE NET Django Web

## ⚠️ ÖNEMLİ: Firebase Admin SDK Credentials

Django projesinin çalışması için **Firebase Admin SDK credentials** gerekli!

### Firebase Credentials İndirme:

1. **Firebase Console'a gidin:**
   ```
   https://console.firebase.google.com/project/kamyonet-e3559/settings/serviceaccounts/adminsdk
   ```

2. **"Generate New Private Key" butonuna tıklayın**

3. **İndirilen JSON dosyasını şu şekilde kaydedin:**
   ```bash
   C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django\firebase-adminsdk.json
   ```

4. **Dosya içeriği şuna benzer olmalı:**
   ```json
   {
     "type": "service_account",
     "project_id": "kamyonet-e3559",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...",
     "client_email": "firebase-adminsdk-...@kamyonet-e3559.iam.gserviceaccount.com",
     ...
   }
   ```

---

## 📋 LOCAL TEST (Önce Yerel Olarak Test Edin)

### 1. Python Virtual Environment

```bash
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"

# Virtual environment oluştur
python -m venv venv

# Aktif et (Windows)
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 2. Firebase Credentials

Firebase Admin SDK dosyasını yukarıdaki adımları takip ederek indirin ve kaydedin.

### 3. Database Migration

```bash
python manage.py migrate
```

### 4. Admin Kullanıcısı (Opsiyonel)

```bash
python manage.py createsuperuser
```

### 5. Test Sunucusu

```bash
python manage.py runserver
```

**Test URL:** http://127.0.0.1:8000

**Test Endpoints:**
- Ana Sayfa: http://127.0.0.1:8000/
- İlanlar: http://127.0.0.1:8000/ilanlar/
- Sitemap: http://127.0.0.1:8000/sitemap.xml
- Admin: http://127.0.0.1:8000/admin/

---

## 🚀 HEROKU DEPLOYMENT

### Gereksinimler:
- Heroku hesabı: https://signup.heroku.com/
- Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

### 1. Heroku CLI Kurulumu

Windows için:
```
https://cli-assets.heroku.com/heroku-x64.exe
```

Kurulum sonrası test:
```bash
heroku --version
```

### 2. Heroku Login

```bash
heroku login
```

### 3. Git Reposu Oluştur

```bash
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
git init
git add .
git commit -m "Initial commit: Django web platform for NAKLIYE NET"
```

### 4. Heroku App Oluştur

```bash
heroku create nakliyenet-web
```

### 5. Ortam Değişkenlerini Ayarla

```bash
# Secret key (üret: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
heroku config:set SECRET_KEY="your-generated-secret-key-here"

# Debug kapalı (production)
heroku config:set DEBUG=False

# Allowed hosts
heroku config:set ALLOWED_HOSTS="nakliyenet-web.herokuapp.com,nakliyenet.com,www.nakliyenet.com"

# Site URL
heroku config:set SITE_URL="https://nakliyenet.com"

# App links (gerçek linkler gelince güncellenecek)
heroku config:set IOS_APP_URL="https://apps.apple.com/app/nakliyenet"
heroku config:set ANDROID_APP_URL="https://play.google.com/store/apps/details?id=com.nakliyenet.app"

# Firebase credentials (Base64 encoded)
# Windows PowerShell:
$content = Get-Content firebase-adminsdk.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)
heroku config:set FIREBASE_CREDENTIALS_BASE64="$base64"
```

### 6. firebase_service.py Güncelle (Base64 desteği için)

```python
# firebase_service.py başına ekle
import base64

def initialize_firebase():
    global _db, _initialized

    if not _initialized:
        # Önce base64'den decode et
        if os.getenv('FIREBASE_CREDENTIALS_BASE64'):
            import json
            import tempfile

            base64_creds = os.getenv('FIREBASE_CREDENTIALS_BASE64')
            decoded = base64.b64decode(base64_creds).decode('utf-8')
            creds_dict = json.loads(decoded)

            cred = credentials.Certificate(creds_dict)
        else:
            # Local development
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-adminsdk.json')
            cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        _initialized = True

    return _db
```

### 7. Deploy!

```bash
git push heroku main
```

### 8. Migration (Production)

```bash
heroku run python manage.py migrate
```

### 9. Logları Kontrol Et

```bash
heroku logs --tail
```

---

## 🌐 DOMAIN AYARLARI

### nakliyenet.com → Heroku

1. **Heroku'da Custom Domain Ekle:**
   ```bash
   heroku domains:add nakliyenet.com
   heroku domains:add www.nakliyenet.com
   ```

2. **DNS Ayarları (Domain sağlayıcınızda):**

   **CNAME Kaydı:**
   ```
   www.nakliyenet.com → nakliyenet-web.herokudns.com
   ```

   **ALIAS veya ANAME Kaydı (Root domain için):**
   ```
   nakliyenet.com → nakliyenet-web.herokudns.com
   ```

   Eğer ALIAS/ANAME desteklemiyorsa, Cloudflare kullanın.

3. **SSL Sertifikası:**
   Heroku otomatik Let's Encrypt sertifikası yükleyecek.

---

## 🔍 GOOGLE SEARCH CONSOLE

### 1. Property Ekle

https://search.google.com/search-console

"Add Property" → "nakliyenet.com"

### 2. Domain Doğrulama

DNS TXT kaydı ekle:
```
TXT google-site-verification=xxxxxx
```

### 3. Sitemap Gönder

```
https://nakliyenet.com/sitemap.xml
```

### 4. URL Inspection

Ana sayfayı ve birkaç ilan sayfasını manuel olarak indexleme isteği gönder.

---

## 📊 MONİTORİNG

### Heroku Metrics

```bash
heroku logs --tail
heroku ps
heroku releases
```

### Sentry (Error Tracking - Opsiyonel)

```bash
pip install sentry-sdk
heroku config:set SENTRY_DSN="your-sentry-dsn"
```

---

## 🔒 GÜVENLİK

### Production Checklist:

- [x] DEBUG=False
- [x] SECRET_KEY güvenli
- [x] ALLOWED_HOSTS doğru
- [x] HTTPS zorunlu
- [x] CSRF protection aktif
- [x] Security headers (settings.py'de)
- [ ] Rate limiting ekle (django-ratelimit)
- [ ] Firewall kuralları

---

## 📱 MOBİL APP ENTEGRASYONU

### Deep Linking Ayarları

1. **Android:**
   ```
   nakliyenet://
   https://nakliyenet.com/ilan/
   ```

2. **iOS:**
   ```
   apple-app-site-association dosyasını ekle
   https://nakliyenet.com/.well-known/apple-app-site-association
   ```

---

## ⚡ PERFORMANS İYİLEŞTİRME

### Sonraki Adımlar:

1. **CDN (Cloudflare):**
   - Static dosyalar için
   - Global cache

2. **Redis Cache:**
   ```bash
   heroku addons:create heroku-redis:mini
   ```

3. **Database (PostgreSQL):**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

---

## 🐛 TROUBLESHOOTING

### "No module named firebase_admin"
```bash
pip install -r requirements.txt
```

### "Firebase credentials not found"
Firebase Admin SDK dosyasını kontrol edin:
```bash
python -c "import os; print(os.path.exists('firebase-adminsdk.json'))"
```

### "Application Error" (Heroku)
```bash
heroku logs --tail
```

### Static files yüklenmiyor
```bash
python manage.py collectstatic --noinput
git add staticfiles
git commit -m "Add static files"
git push heroku main
```

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Firebase Admin SDK credentials indirildi
- [ ] `.env` dosyası oluşturuldu
- [ ] Local olarak test edildi (runserver)
- [ ] Git reposu oluşturuldu
- [ ] Heroku app oluşturuldu
- [ ] Ortam değişkenleri ayarlandı
- [ ] Deploy edildi (git push heroku main)
- [ ] Migration yapıldı (heroku run migrate)
- [ ] Domain bağlandı
- [ ] SSL sertifikası aktif
- [ ] Google Search Console'a eklendi
- [ ] Sitemap gönderildi

---

## 📞 DESTEK

Sorun yaşarsanız:
1. `heroku logs --tail` ile logları kontrol edin
2. Local'de test edin
3. Firebase credentials'ı doğrulayın

---

## 🎉 SONUÇ

Deployment tamamlandığında:
- ✅ https://nakliyenet.com → Django SEO sayfaları
- ✅ https://nakliyenet.com/sitemap.xml → Google indexleme
- ✅ Flutter app → Aynı Firebase kullanıyor
- ✅ Deep linking → Web ↔ App entegrasyonu

**6 ayda 3-5x organik trafik artışı beklenir!** 🚀
