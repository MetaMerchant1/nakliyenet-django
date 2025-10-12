# ⚡ HIZLI BAŞLANGIÇ - NAKLIYE NET Django

## 🎯 YAPILMASI GEREKENLER (Sırayla)

### 1️⃣ Firebase Admin SDK Credentials İNDİR ⚠️ EN ÖNEMLİ!

**Şu anda eksik olan tek şey bu dosya!**

1. Tarayıcıda aç:
   ```
   https://console.firebase.google.com/project/kamyonet-e3559/settings/serviceaccounts/adminsdk
   ```

2. **"Generate New Private Key"** butonuna tıkla

3. İndirilen dosyayı şu isimle kaydet:
   ```
   firebase-adminsdk.json
   ```

4. Dosyayı şuraya taşı:
   ```
   C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django\firebase-adminsdk.json
   ```

---

### 2️⃣ LOCAL TEST (5 Dakika)

```bash
# Terminal aç ve şu komutları çalıştır:

cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"

# Virtual environment
python -m venv venv
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Database
python manage.py migrate

# Çalıştır
python manage.py runserver
```

**Test et:** http://127.0.0.1:8000

✅ Ana sayfa açılıyor mu?
✅ http://127.0.0.1:8000/ilanlar/ çalışıyor mu?
✅ http://127.0.0.1:8000/sitemap.xml oluşuyor mu?

---

### 3️⃣ HEROKU DEPLOYMENT (10 Dakika)

#### A) Heroku CLI Kur

Windows için indir:
```
https://cli-assets.heroku.com/heroku-x64.exe
```

Kurulum sonrası test:
```bash
heroku --version
```

#### B) Heroku Login

```bash
heroku login
```

#### C) App Oluştur

```bash
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
heroku create nakliyenet-web
```

#### D) Firebase Credentials Gönder

**PowerShell'de çalıştır:**

```powershell
# firebase-adminsdk.json dosyasını base64'e çevir
$content = Get-Content firebase-adminsdk.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)

# Heroku'ya gönder
heroku config:set FIREBASE_CREDENTIALS_BASE64="$base64"
```

#### E) Diğer Ayarlar

```bash
# Secret key üret
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Çıkan sonucu kopyala ve şu komutu çalıştır (KEY yerine yapıştır):
heroku config:set SECRET_KEY="BURAYA_KOPYALADIĞIN_KEY"

# Debug kapalı
heroku config:set DEBUG=False

# Allowed hosts
heroku config:set ALLOWED_HOSTS="nakliyenet-web.herokuapp.com,nakliyenet.com,www.nakliyenet.com"
```

#### F) Deploy!

```bash
git push heroku main
```

#### G) Migration

```bash
heroku run python manage.py migrate
```

#### H) Test

Heroku URL'ini aç:
```bash
heroku open
```

Veya:
```
https://nakliyenet-web.herokuapp.com
```

---

### 4️⃣ DOMAIN BAĞLA (nakliyenet.com)

#### A) Heroku'da Domain Ekle

```bash
heroku domains:add nakliyenet.com
heroku domains:add www.nakliyenet.com
```

Heroku DNS bilgisini göster:
```bash
heroku domains
```

Çıktı:
```
=== nakliyenet-web Heroku Domain
nakliyenet-web.herokudns.com

=== nakliyenet-web Custom Domains
Domain Name          DNS Target
─────────────────   ──────────────────────────────
nakliyenet.com       nakliyenet-web.herokudns.com
www.nakliyenet.com   nakliyenet-web.herokudns.com
```

#### B) DNS Ayarları (Domain Panel'de)

Domain sağlayıcınızın (GoDaddy, Namecheap vb.) paneline gir:

**CNAME Kaydı Ekle:**
```
Tip: CNAME
Name: www
Value: nakliyenet-web.herokudns.com
TTL: 3600
```

**A Kaydı veya ALIAS Ekle:**
```
Eğer ALIAS destekliyorsa:
Tip: ALIAS
Name: @
Value: nakliyenet-web.herokudns.com

Eğer ALIAS desteklemiyorsa:
Cloudflare kullan (ücretsiz)
```

#### C) SSL Bekle (5-30 dakika)

Heroku otomatik Let's Encrypt sertifikası yükleyecek.

Kontrol et:
```bash
heroku certs:auto:enable
```

---

### 5️⃣ GOOGLE SEARCH CONSOLE

#### A) Property Ekle

1. https://search.google.com/search-console
2. **"Add Property"**
3. Domain: `nakliyenet.com`

#### B) Doğrulama

DNS TXT kaydı ekle (Google verecek):
```
Tip: TXT
Name: @
Value: google-site-verification=xxxxxxxxxxxxx
```

#### C) Sitemap Gönder

Search Console'da:
- Sitemaps → Add new sitemap
- URL: `https://nakliyenet.com/sitemap.xml`
- Submit

#### D) URL Inspection

Ana sayfayı manuel indexleme isteği gönder:
```
https://nakliyenet.com/
```

---

## ✅ TAMAMLANDI CHECKLIST

- [ ] Firebase Admin SDK credentials indirildi (`firebase-adminsdk.json`)
- [ ] Local'de test edildi (`python manage.py runserver`)
- [ ] Heroku CLI kuruldu
- [ ] Heroku'ya deploy edildi (`git push heroku main`)
- [ ] Firebase credentials Heroku'ya yüklendi
- [ ] Heroku'da çalıştığı test edildi (`heroku open`)
- [ ] Domain bağlandı (nakliyenet.com)
- [ ] DNS ayarları yapıldı
- [ ] SSL sertifikası aktif
- [ ] Google Search Console'a eklendi
- [ ] Sitemap gönderildi

---

## 🐛 SORUN ÇÖZME

### "Firebase credentials not found"

`firebase-adminsdk.json` dosyası eksik. Adım 1'i tekrar yap.

### Local'de çalışıyor ama Heroku'da hata

```bash
heroku logs --tail
```

Log'larda hatayı göreceksin. Muhtemelen Firebase credentials eksiktir:

```bash
# PowerShell ile tekrar gönder
$content = Get-Content firebase-adminsdk.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)
heroku config:set FIREBASE_CREDENTIALS_BASE64="$base64"
```

### "No such file or directory: 'venv'"

```bash
python -m venv venv
```

### SSL sertifikası yüklenmiyor

30 dakika bekle. Hala yüklenmezse:

```bash
heroku certs:auto:refresh
```

---

## 📊 BEKLENEN SONUÇLAR

### Hemen:
- ✅ https://nakliyenet.com → Django SEO sayfaları
- ✅ /sitemap.xml → Dinamik sitemap
- ✅ Google indexlemeye başlar
- ✅ Flutter app → Aynı Firebase kullanıyor

### 1 Hafta Sonra:
- 📈 Google'da ilk sayfalar indexlendi
- 📈 Sitemap verify edildi

### 1 Ay Sonra:
- 📈 İlanlar Google'da görünmeye başladı
- 📈 Organik trafik artışı

### 6 Ay Sonra:
- 🚀 **3-5x organik trafik artışı**
- 🚀 Google'da üst sıralarda
- 🚀 Rich results (yıldız, fiyat vb.)

---

## 🎯 ÖNCELİK SIRASI

1. ⚠️ **EN ÖNEMLİ:** `firebase-adminsdk.json` indir
2. 🧪 Local test yap
3. 🚀 Heroku'ya deploy et
4. 🌐 Domain bağla
5. 📊 Google Search Console

**Tahmini Süre: 30 dakika**

---

## 📞 YARDIM

Takıldığın yer olursa:

1. `DEPLOYMENT_GUIDE.md` dosyasına bak (detaylı)
2. `heroku logs --tail` ile log'ları kontrol et
3. Firebase credentials'ı doğrula

---

**Başarılar! 🚀**
