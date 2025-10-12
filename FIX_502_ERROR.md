# 🔴 502 Error - Django Başlamıyor

**Hata:** `HTTP ERROR 502`
**Anlam:** Sunucu çalışamıyor (büyük ihtimalle environment variables eksik)

---

## 🔍 SORUN NEDİR?

502 hatası genelde şu sebeplerden olur:

1. **Environment variables eksik** ⚠️ EN MUHTEMEL
2. Firebase credentials yanlış
3. Django settings hatası
4. Port hatası

---

## ✅ ÇÖZÜM ADIMLARI

### 1️⃣ Render Logs'u Kontrol Et

**Render Dashboard'da:**

1. Service sayfanıza gidin
2. **"Logs"** sekmesine tıklayın
3. En alttaki hata mesajını bulun

**Aranacak hatalar:**

```
❌ KeyError: 'SECRET_KEY'
❌ ImproperlyConfigured
❌ Firebase credentials not found
❌ ModuleNotFoundError
```

---

### 2️⃣ Environment Variables Kontrol

**Render Dashboard → Settings → Environment**

**Olması gerekenler (5 tane):**

#### ✅ DEBUG
```
Key: DEBUG
Value: False
```

#### ✅ SECRET_KEY
```
Key: SECRET_KEY
Value: $5bw)o!40dmbmn!87$v(uh#=o7mm3rg=o8jm@6-u_a11_fa@yq
```

#### ✅ ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: .onrender.com,nakliyenet.com,www.nakliyenet.com
```

#### ✅ PYTHON_VERSION
```
Key: PYTHON_VERSION
Value: 3.11.5
```

#### ⚠️ FIREBASE_CREDENTIALS_BASE64 (EN ÖNEMLİ!)
```
Key: FIREBASE_CREDENTIALS_BASE64
Value: [UZUN BASE64 STRING]
```

**Eğer eksikse veya yanlışsa:**
1. **Add Environment Variable** tıkla
2. Yukardakileri ekle
3. **Save Changes**
4. Otomatik redeploy başlar

---

### 3️⃣ Firebase Credentials Base64 Oluştur

**Eğer FIREBASE_CREDENTIALS_BASE64 yoksa veya yanlışsa:**

PowerShell'de:
```powershell
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
.\generate_base64.ps1
```

**Çıkan UZUN metni kopyala** (tamamını!)

Render'da:
- Environment → Edit FIREBASE_CREDENTIALS_BASE64
- Kopyaladığın değeri yapıştır
- Save

---

### 4️⃣ Build & Start Command Kontrol

**Render Dashboard → Settings → Build & Deploy**

**Build Command (doğru ✅):**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command (doğru ✅):**
```
gunicorn nakliyenet.wsgi:application
```

Eğer farklıysa düzelt ve **Save Changes**

---

### 5️⃣ Manuel Redeploy

Environment variables'ları ekledikten sonra:

1. **Manual Deploy** → **Clear build cache & deploy**
2. Logs'u takip et
3. Şunu görene kadar bekle:
   ```
   ==> Your service is live 🎉
   ```

---

## 🐛 LOGS'DA GÖREBILECEĞINIZ HATALAR

### Hata 1: ImproperlyConfigured
```
django.core.exceptions.ImproperlyConfigured:
The SECRET_KEY setting must not be empty.
```

**Çözüm:** `SECRET_KEY` environment variable ekle

---

### Hata 2: Firebase Credentials
```
ValueError: Could not load credentials
```

**Çözüm:** `FIREBASE_CREDENTIALS_BASE64` environment variable ekle (doğru base64 string ile)

---

### Hata 3: ALLOWED_HOSTS
```
DisallowedHost at /
Invalid HTTP_HOST header: 'nakliyenet-web.onrender.com'
```

**Çözüm:** `ALLOWED_HOSTS` environment variable ekle

---

### Hata 4: Port Error
```
Error: Cannot bind to 0.0.0.0:10000
```

**Çözüm:** Render otomatik port verir, PORT environment variable eklemeyin!

---

## 📋 KOMPLE ENVIRONMENT VARIABLES LİSTESİ

Render Settings → Environment → Add Environment Variable:

```
DEBUG=False
SECRET_KEY=$5bw)o!40dmbmn!87$v(uh#=o7mm3rg=o8jm@6-u_a11_fa@yq
ALLOWED_HOSTS=.onrender.com,nakliyenet.com,www.nakliyenet.com
PYTHON_VERSION=3.11.5
FIREBASE_CREDENTIALS_BASE64=[generate_base64.ps1 çıktısı]
```

**Not:** Her satır ayrı bir variable!

---

## 🔄 ADIM ADIM FIX

### Adım 1: Logs'a Bak
```
Render Dashboard → Logs sekmesi
En alt satırdaki hatayı bul
```

### Adım 2: Environment Variables Ekle
```
Settings → Environment
Yukardaki 5 variable'ı ekle
```

### Adım 3: Firebase Base64 Oluştur
```powershell
cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
.\generate_base64.ps1
# Çıktıyı kopyala
```

### Adım 4: Render'a Ekle
```
Environment → Add Environment Variable
Key: FIREBASE_CREDENTIALS_BASE64
Value: [Kopyaladığın base64]
Save
```

### Adım 5: Redeploy
```
Manual Deploy → Clear build cache & deploy
```

### Adım 6: Test
```
https://nakliyenet-web.onrender.com
```

---

## ⚡ HIZLI FIX (En Muhtemel Sorun)

**FIREBASE_CREDENTIALS_BASE64 eksik!**

1. PowerShell aç:
   ```powershell
   cd "C:\Users\Ekrem\Desktop\Kamyonet app\nakliyenet_django"
   .\generate_base64.ps1
   ```

2. Çıkan metni TAMAMINI kopyala (2000+ karakter)

3. Render → Settings → Environment → Add Environment Variable
   ```
   Key: FIREBASE_CREDENTIALS_BASE64
   Value: [Yapıştır]
   ```

4. Save → Otomatik redeploy başlar

5. 5 dakika bekle → Test et!

---

## 📞 HALA ÇALIŞMIYOR MU?

**Logs'tan şu bilgileri paylaşın:**

1. En son satırdaki hata mesajı
2. Traceback varsa son 10 satır
3. Environment variables ekli mi? (screenshot)

**Render Logs'a nasıl bakılır:**

```
Dashboard → nakliyenet-web → Logs sekmesi
En alta scroll et
Kırmızı hata mesajlarını bul
```

---

**Şimdi Render Logs'una bakın ve hata mesajını paylaşın!**
