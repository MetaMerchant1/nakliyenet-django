# 🚀 RENDER DEPLOYMENT - ŞİMDİ YAPILACAKLAR

**GitHub Repository:** ✅ https://github.com/MetaMerchant1/nakliyenet-django

**Durum:** GitHub'a push başarılı! Şimdi Render'da deployment yapabiliriz.

---

## 📋 RENDER'DA DEPLOYMENT ADIMLARI

### 1️⃣ Render Dashboard'a Git

https://dashboard.render.com

### 2️⃣ New Web Service Oluştur

1. **"New +"** butonuna tıkla (sağ üstte)
2. **"Web Service"** seç
3. GitHub ile bağlan (ilk defa ise **"Connect GitHub"** de)

### 3️⃣ Repository Seç

Repository listesinden:
```
MetaMerchant1/nakliyenet-django
```
seçin ve **"Connect"** tıkla

### 4️⃣ Temel Ayarlar

**Name:**
```
nakliyenet-web
```

**Region:**
```
Frankfurt (EU Central)
```
(veya size yakın olan)

**Branch:**
```
main
```

**Root Directory:**
```
(boş bırak)
```

**Runtime:**
```
Python 3
```

### 5️⃣ Build & Start Commands

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```
gunicorn nakliyenet.wsgi:application
```

---

## ⚙️ ENVIRONMENT VARIABLES (ÖNEMLİ!)

**"Advanced"** butonuna tıklayın, sonra **"Add Environment Variable"** ile ekleyin:

### Variable 1: DEBUG
```
Key: DEBUG
Value: False
```

### Variable 2: SECRET_KEY
```
Key: SECRET_KEY
Value: $5bw)o!40dmbmn!87$v(uh#=o7mm3rg=o8jm@6-u_a11_fa@yq
```

### Variable 3: ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: .onrender.com,nakliyenet.com,www.nakliyenet.com
```

### Variable 4: PYTHON_VERSION
```
Key: PYTHON_VERSION
Value: 3.11.5
```

### Variable 5: FIREBASE_CREDENTIALS_BASE64 ⚠️ EN ÖNEMLİ

**PowerShell'de şu komutu çalıştırın:**

```powershell
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
.\generate_base64.ps1
```

Çıkan **UZUN base64 metni** kopyalayın ve Render'a ekleyin:

```
Key: FIREBASE_CREDENTIALS_BASE64
Value: [BURAYA_KOPYALADIĞINIZ_UZUN_BASE64_METNİ]
```

**Not:** Bu değer çok uzun (2000+ karakter). Tamamını kopyaladığınızdan emin olun!

---

## 💰 PLAN SEÇİMİ

**Free Plan** seçin (başlangıç için yeterli)

**Özellikler:**
- ✅ Ücretsiz
- ✅ 750 saat/ay
- ⚠️ 15 dakika inaktif kalırsa uyur (ilk istek 30 saniye sürer)
- ✅ Otomatik SSL

**İlerleyen zamanda upgrade edebilirsiniz ($7/ay)**

---

## 🚀 CREATE WEB SERVICE!

Tüm ayarları yaptıktan sonra:

**"Create Web Service"** butonuna tıklayın!

---

## 📊 DEPLOYMENT TAKİBİ

Deployment başladı!

### Logs'u Takip Edin

**"Logs"** sekmesine geçin. Şunları göreceksiniz:

```
==> Cloning from https://github.com/MetaMerchant1/nakliyenet-django...
==> Using Python version 3.11.5
==> Installing dependencies from requirements.txt
==> Collecting Django==4.2.8
==> Installing collected packages...
==> Successfully installed...
==> Running collectstatic...
==> Starting gunicorn...
==> Your service is live 🎉
```

**Süre:** 5-10 dakika

### Başarılı Deployment

Logs'ta şunu görünce deployment başarılı demektir:
```
==> Your service is live at https://nakliyenet-web.onrender.com
```

---

## ✅ TEST ET!

Site yayına girince test edin:

### Ana Sayfa
```
https://nakliyenet-web.onrender.com/
```

### İlan Listesi
```
https://nakliyenet-web.onrender.com/ilanlar/
```

### Sitemap (SEO için önemli)
```
https://nakliyenet-web.onrender.com/sitemap.xml
```

---

## 🐛 SORUN GİDERME

### Build Hatası Alırsanız

**Logs'ta hata görürseniz:**

1. Environment variables'ları kontrol edin
   - Özellikle FIREBASE_CREDENTIALS_BASE64 tam kopyalandı mı?

2. **"Manual Deploy"** → **"Clear build cache & deploy"**

3. Hata mesajını okuyun, genelde ne eksik olduğunu söyler

### Firebase Connection Hatası

**Logs'ta "Firebase error" görürseniz:**

Base64 değeri doğru mu kontrol edin:
```powershell
# PowerShell'de
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
.\generate_base64.ps1
```

Çıktıyı tekrar kopyalayıp Render'da **Environment Variables** → **Edit** → FIREBASE_CREDENTIALS_BASE64 değerini güncelleyin

### Site Açılmıyor

**Free plan 15 dakika sonra uyur.**

İlk istek 30-60 saniye sürebilir, normal!

Sayfayı yenileyin, 2. istekte hızlı açılır.

---

## 🎯 DEPLOYMENT SONRASI

Site yayına girdikten sonra:

### 1. Domain Bağlama (Opsiyonel)

nakliyenet.com → Render'a bağlamak için:

**Render'da:**
- Settings → Custom Domain → Add Custom Domain
- `nakliyenet.com` ve `www.nakliyenet.com` ekle

**Domain Provider'da:**
- CNAME kaydı ekle: `www` → `nakliyenet-web.onrender.com`
- CNAME kaydı ekle: `@` → `nakliyenet-web.onrender.com`

### 2. Google Search Console

1. https://search.google.com/search-console
2. Add Property → `nakliyenet.com`
3. DNS doğrulama yap
4. Sitemap gönder: `https://nakliyenet.com/sitemap.xml`

### 3. Flutter Deep Linking

Mobil uygulamalarınızı web sitesine bağlayın:
- [FLUTTER_DEEP_LINKING.md](FLUTTER_DEEP_LINKING.md)

---

## 🔄 OTOMATIK DEPLOYMENT

**Artık her GitHub push otomatik deploy olacak!**

Kod değiştirdiğinizde:
```bash
git add .
git commit -m "Update something"
git push origin main
```

Render otomatik olarak yeni versiyonu deploy eder! 🚀

---

## 📞 YARDIM

**Deployment sırasında sorun olursa:**

1. Logs'u dikkatlice okuyun
2. Environment variables'ları kontrol edin
3. [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) → Detaylı rehber

---

## 🎉 ÖZET

**Şu ana kadar:**
- ✅ Django projesi hazır
- ✅ Local test başarılı
- ✅ GitHub'a push edildi
- ⏳ Render'da deployment başlatılacak

**Sonraki adım:**
1. Render'da yukarıdaki ayarları yap
2. Environment variables ekle
3. Create Web Service tıkla
4. 10 dakika bekle
5. Site yayında! 🎉

**Başarılar! 🚀**
