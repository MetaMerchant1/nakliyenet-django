# 🚀 DEPLOYMENT CHECKLIST - NAKLIYE NET

## ✅ TAMAMLANAN İŞLER

- [x] Django projesi kurulumu
- [x] Firebase entegrasyon kodu (firebase_service.py)
- [x] SEO-optimize template'ler (8 HTML dosyası)
- [x] Dinamik sitemap yapılandırması
- [x] Deep linking hazırlığı
- [x] Heroku deployment dosyaları (Procfile, runtime.txt)
- [x] requirements.txt bağımlılıkları
- [x] .env yapılandırması
- [x] Git repository oluşturuldu ve commit edildi
- [x] Detaylı dokümantasyon (QUICKSTART.md, DEPLOYMENT_GUIDE.md)

---

## ⚠️ DEPLOYMENT İÇİN GEREKLİ ADIMLAR

### 1. Firebase Admin SDK Credentials İNDİR (5 dakika) ⚠️⚠️⚠️

**EN ÖNEMLİ ADIM - Önce bu yapılmalı!**

1. Tarayıcıda aç:
   ```
   https://console.firebase.google.com/project/kamyonet-e3559/settings/serviceaccounts/adminsdk
   ```

2. **"Generate New Private Key"** butonuna tıkla

3. İndirilen dosyayı **`firebase-adminsdk.json`** olarak kaydet

4. Dosyayı şu klasöre taşı:
   ```
   C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django\firebase-adminsdk.json
   ```

---

### 2. LOCAL TEST (5 dakika)

Local'de çalıştığını doğrula:

```bash
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"

# Virtual environment oluştur
python -m venv venv
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Database migrate
python manage.py migrate

# Çalıştır
python manage.py runserver
```

**Test Et:**
- [ ] http://127.0.0.1:8000 → Ana sayfa açılıyor mu?
- [ ] http://127.0.0.1:8000/ilanlar/ → İlan listesi çalışıyor mu?
- [ ] http://127.0.0.1:8000/sitemap.xml → Sitemap oluşuyor mu?

---

### 3. HEROKU DEPLOYMENT (15 dakika)

**Adım 3.1: Heroku CLI Kur**

Windows için:
```
https://cli-assets.heroku.com/heroku-x64.exe
```

İndirip kur, sonra test et:
```bash
heroku --version
```

**Adım 3.2: Heroku Login**

```bash
heroku login
```

**Adım 3.3: Heroku App Oluştur**

```bash
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
heroku create nakliyenet-web
```

**Adım 3.4: Firebase Credentials'ı Base64'e Çevir ve Heroku'ya Gönder**

PowerShell'de çalıştır:
```powershell
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"

# Firebase credentials'ı base64'e çevir
$content = Get-Content firebase-adminsdk.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)

# Heroku'ya gönder
heroku config:set FIREBASE_CREDENTIALS_BASE64="$base64"
```

**Adım 3.5: Secret Key Üret ve Gönder**

```bash
# Secret key üret
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Çıkan sonucu kopyala ve şu komutu çalıştır:
heroku config:set SECRET_KEY="BURAYA_ÜRETILEN_KEY"

# Debug kapalı
heroku config:set DEBUG=False

# Allowed hosts
heroku config:set ALLOWED_HOSTS="nakliyenet-web.herokuapp.com,nakliyenet.com,www.nakliyenet.com"
```

**Adım 3.6: Deploy!**

```bash
git push heroku master
```

**Adım 3.7: Migration Çalıştır**

```bash
heroku run python manage.py migrate
```

**Adım 3.8: Test Et**

```bash
heroku open
```

Veya tarayıcıda aç:
```
https://nakliyenet-web.herokuapp.com
```

---

### 4. DOMAIN BAĞLA (10 dakika)

**Adım 4.1: Heroku'da Domain Ekle**

```bash
heroku domains:add nakliyenet.com
heroku domains:add www.nakliyenet.com
```

**Adım 4.2: DNS Bilgisini Al**

```bash
heroku domains
```

Çıktıda göreceğin **DNS Target**: `nakliyenet-web.herokudns.com`

**Adım 4.3: Domain Provider'da DNS Ayarları**

Domain sağlayıcının (GoDaddy, Namecheap vb.) paneline gir:

**CNAME Kaydı:**
```
Tip: CNAME
Name: www
Value: nakliyenet-web.herokudns.com
TTL: 3600
```

**A Kaydı veya ALIAS:**
```
Cloudflare kullanıyorsan:
  Tip: CNAME
  Name: @
  Value: nakliyenet-web.herokudns.com
  Proxy: Kapalı

Cloudflare kullanmıyorsan:
  Cloudflare'e geç (ücretsiz) veya domain sağlayıcının ALIAS desteği varsa kullan
```

**Adım 4.4: SSL Sertifikası Aktifleştir**

```bash
heroku certs:auto:enable
```

5-30 dakika içinde Let's Encrypt sertifikası otomatik yüklenecek.

---

### 5. GOOGLE SEARCH CONSOLE (5 dakika)

**Adım 5.1: Property Ekle**

1. https://search.google.com/search-console
2. **"Add Property"**
3. Domain: `nakliyenet.com`

**Adım 5.2: Doğrulama**

Google'ın vereceği DNS TXT kaydını domain provider'a ekle:
```
Tip: TXT
Name: @
Value: google-site-verification=xxxxxxxxxxxxx
```

**Adım 5.3: Sitemap Gönder**

Search Console'da:
- **Sitemaps** → **Add new sitemap**
- URL: `https://nakliyenet.com/sitemap.xml`
- **Submit**

**Adım 5.4: URL Inspection**

Ana sayfayı manuel indexleme için gönder:
```
https://nakliyenet.com/
```

---

## 📊 BEKLENEN SONUÇLAR

### İlk Gün:
- ✅ Site yayında: https://nakliyenet.com
- ✅ Sitemap Google'a gönderildi
- ✅ SSL sertifikası aktif (HTTPS)

### 1 Hafta Sonra:
- 📈 Google ilk sayfaları indexlemeye başladı
- 📈 Search Console'da ilk veriler görünüyor

### 1 Ay Sonra:
- 📈 İlanlar Google'da görünmeye başladı
- 📈 İlk organik trafik geliyor

### 6 Ay Sonra:
- 🚀 **3-5x organik trafik artışı**
- 🚀 Anahtar kelimelerde üst sıralarda
- 🚀 Rich results (yıldız, fiyat vb.)

---

## 🆘 SORUN GİDERME

### Firebase credentials bulunamıyor
```bash
# Local'de kontrol et:
dir firebase-adminsdk.json

# Heroku'da kontrol et:
heroku config:get FIREBASE_CREDENTIALS_BASE64
```

### Heroku'da hata
```bash
# Log'ları kontrol et:
heroku logs --tail
```

### Domain çalışmıyor
- DNS değişikliği 5 dakika - 48 saat sürebilir
- Kontrol: https://dnschecker.org

### SSL sertifikası yüklenmiyor
- 30 dakika bekle
- Manuel yenileme: `heroku certs:auto:refresh`

---

## 📞 YARDIM KAYNAKLARI

1. **QUICKSTART.md** → Hızlı başlangıç (30 dakika)
2. **DEPLOYMENT_GUIDE.md** → Detaylı deployment
3. **FLUTTER_DEEP_LINKING.md** → Mobil entegrasyon
4. **PROJE_OZETI.md** → Proje özeti

---

## 🎯 ŞU ANDA NEREDESINIZ?

```
[✅] Django Projesi Hazır
[⏳] Firebase Credentials İNDİR    ← ŞİMDİ BURADASINIZ
[ ] Local Test
[ ] Heroku Deployment
[ ] Domain Bağlama
[ ] Google Search Console
```

**Sonraki adım:** Firebase Admin SDK credentials dosyasını indirin!

**Link:**
```
https://console.firebase.google.com/project/kamyonet-e3559/settings/serviceaccounts/adminsdk
```

---

**🚀 Başarılar! Sorularınız olursa QUICKSTART.md dosyasına bakın.**
