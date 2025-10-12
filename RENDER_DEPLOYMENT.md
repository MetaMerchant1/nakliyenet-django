# 🚀 RENDER DEPLOYMENT REHBERİ

**Tarih:** 8 Ekim 2025
**Platform:** Render.com
**Avantaj:** CLI gerektirmiyor, web panelden deployment!

---

## 📋 ADIM ADIM DEPLOYMENT

### 1️⃣ YENİ WEB SERVİSİ OLUŞTUR

Render dashboard'da:

1. **"New +"** butonuna tıkla (sağ üstte)
2. **"Web Service"** seç
3. GitHub repository'nizi seçin: `nakliyenet_django`

---

### 2️⃣ BUILD AYARLARI

Aşağıdaki bilgileri girin:

**Name:**
```
nakliyenet-web
```

**Region:**
```
Frankfurt (EU Central)
```
(veya en yakın bölge)

**Branch:**
```
master
```

**Root Directory:**
```
(boş bırak)
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```
gunicorn nakliyenet.wsgi:application
```

---

### 3️⃣ ENVIRONMENT VARIABLES (ÖNEMLİ!)

**"Advanced"** sekmesine geç ve şu environment variable'ları ekle:

#### 3.1 DEBUG
```
Key: DEBUG
Value: False
```

#### 3.2 SECRET_KEY

**Yeni terminal açın ve şu komutu çalıştırın:**
```bash
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Çıkan sonucu kopyalayın ve Render'a ekleyin:
```
Key: SECRET_KEY
Value: [KOPYALADIĞINIZ_KEY]
```

#### 3.3 ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: .onrender.com,nakliyenet.com,www.nakliyenet.com
```

#### 3.4 FIREBASE_CREDENTIALS_BASE64

**PowerShell'de şu komutu çalıştırın:**
```powershell
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"

$content = Get-Content firebase-adminsdk.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)

# Ekrana yazdır (kopyala)
Write-Output $base64
```

Çıkan UZUN metni kopyala ve Render'a ekle:
```
Key: FIREBASE_CREDENTIALS_BASE64
Value: [KOPYALADIĞINIZ_BASE64_STRING]
```

#### 3.5 PYTHON_VERSION
```
Key: PYTHON_VERSION
Value: 3.11.5
```

---

### 4️⃣ PLAN SEÇİMİ

**Free Plan** seçin (başlangıç için yeterli)

**Özellikler:**
- ✅ Ücretsiz
- ✅ 750 saat/ay
- ⚠️ 15 dakika inaktiflikten sonra uyur (ilk istek yavaş)
- ✅ Otomatik SSL sertifikası

**Ücretli plan (opsiyonel - $7/ay):**
- ✅ Her zaman aktif
- ✅ Daha hızlı
- ✅ Daha fazla memory

---

### 5️⃣ CREATE WEB SERVICE

**"Create Web Service"** butonuna tıkla!

**Deployment başladı! ⏳**

İlk deployment 5-10 dakika sürer.

---

## 📊 DEPLOYMENT DURUMU

### Takip Et

Render dashboard'da:
- **Logs** sekmesi → Build ve deployment logları
- **Events** sekmesi → Deployment geçmişi

### Başarılı Deployment Göstergeleri

**Logs'ta göreceksiniz:**
```
==> Installing dependencies...
==> Collecting static files...
==> Starting gunicorn...
==> Your service is live 🎉
```

---

## 🌐 SİTE URL'İ

Deployment başarılı olunca:

```
https://nakliyenet-web.onrender.com
```

Bu URL'e gidin ve test edin!

---

## ✅ DOĞRULAMA

Site yayına girdiğinde test edin:

1. **Ana sayfa:**
   ```
   https://nakliyenet-web.onrender.com/
   ```

2. **İlan listesi:**
   ```
   https://nakliyenet-web.onrender.com/ilanlar/
   ```

3. **Sitemap:**
   ```
   https://nakliyenet-web.onrender.com/sitemap.xml
   ```

---

## 🔧 SORUN GİDERME

### Build Hatası

**Logs'ta hata görürseniz:**

1. **"Manual Deploy"** → **"Clear build cache & deploy"**
2. Environment variables'ları kontrol edin
3. FIREBASE_CREDENTIALS_BASE64 doğru kopyalandı mı?

### Firebase Connection Hatası

**Test için PowerShell'de:**
```powershell
$base64 = "BURAYA_BASE64_STRING"
$bytes = [System.Convert]::FromBase64String($base64)
$json = [System.Text.Encoding]::UTF8.GetString($bytes)
Write-Output $json
```

JSON çıktısı görmelisiniz.

### Site Yavaş

Free plan 15 dakika sonra uyur. İlk istek 30-60 saniye sürebilir.

**Çözüm:**
- Ücretli plana geç ($7/ay)
- veya cron job ile 10 dakikada bir ping at

---

## 🔄 OTOMATIK DEPLOYMENT

**Artık her git push otomatik deploy olacak!**

```bash
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
git add .
git commit -m "Update something"
git push origin master
```

Render otomatik olarak yeni versiyonu deploy eder! 🚀

---

## 🌍 CUSTOM DOMAIN BAĞLAMA

### Render'da Domain Ekle

1. Web service settings → **"Custom Domain"**
2. **Add Custom Domain:**
   ```
   nakliyenet.com
   www.nakliyenet.com
   ```

3. Render size DNS bilgilerini verecek

### Domain Provider'da DNS Ayarları

**CNAME Kayıtları Ekle:**

```
Type: CNAME
Name: www
Value: nakliyenet-web.onrender.com
TTL: 3600
```

```
Type: CNAME
Name: @
Value: nakliyenet-web.onrender.com
TTL: 3600
```

**Not:** Bazı domain sağlayıcılar @ için CNAME desteklemez. O zaman:
- Cloudflare kullanın (ücretsiz)
- veya ALIAS kaydı kullanın

### SSL Sertifikası

Render otomatik olarak Let's Encrypt SSL sertifikası kurar.

5-30 dakika içinde HTTPS aktif olur.

---

## 📈 SONRAKI ADIMLAR

### 1. Google Search Console

1. https://search.google.com/search-console
2. **"Add Property"** → `nakliyenet.com`
3. DNS TXT kaydı ile doğrula
4. Sitemap gönder: `https://nakliyenet.com/sitemap.xml`

### 2. Flutter Deep Linking

Mobil uygulamalarınızı web sitesine bağlayın:
- [FLUTTER_DEEP_LINKING.md](FLUTTER_DEEP_LINKING.md)

### 3. Monitoring

Render dashboard'dan:
- CPU/Memory kullanımı
- Request sayısı
- Error logları

---

## 💰 MALİYET

**Free Plan:**
- ✅ 750 saat/ay ücretsiz
- ✅ Küçük projeler için ideal
- ⚠️ 15 dakika inaktiflikten sonra uyur

**Starter Plan ($7/ay):**
- ✅ Her zaman aktif
- ✅ Daha hızlı
- ✅ 512 MB RAM
- ✅ Profesyonel siteler için

**Tavsiye:** Free plan ile başlayın, trafik artınca upgrade edin.

---

## 🎯 ÖZET

**Şu ana kadar:**
- ✅ Django projesi hazır
- ✅ GitHub'a bağlandı
- ⏳ Render'da deployment başladı

**Beklenen süre:** 5-10 dakika

**Sonraki adım:** Deployment tamamlanınca URL'i test edin!

---

## 📞 YARDIM

**Deployment sırasında sorun olursa:**
1. Render logs'u kontrol edin
2. Environment variables'ları kontrol edin
3. [QUICKSTART.md](QUICKSTART.md) → Sorun giderme

**Başarılar! 🚀**
