# <Ø Sadece 3 Bilgi Kald1! (5 Dakika)

Firebase Admin SDK'dan otomatik olarak _unlar1 doldurdum:

 `FIREBASE_PROJECT_ID` = kamyonet-e3559
 `FIREBASE_AUTH_DOMAIN` = kamyonet-e3559.firebaseapp.com
 `FIREBASE_STORAGE_BUCKET` = kamyonet-e3559.appspot.com

**Sadece 3 bilgi daha laz1m:**

---

## 1„ FIREBASE_API_KEY (2 dakika)

### Ad1mlar:
1. Taray1c1da aÁ: https://console.firebase.google.com/project/kamyonet-e3559/settings/general
   - (Otomatik olarak doru projeye gider)
2. A_a1 kayd1r í **"Your apps"** bˆl¸m¸
3. Web app (`</>`) varsa t1kla
   - Yoksa: **"Add app"** í Web í Register
4. **"SDK setup and configuration"** alt1nda `apiKey` deerini kopyala

### ÷rnek:
```javascript
apiKey: "AIzaSyABCDEF123456..."  // ê Bunu kopyala
```

### .env'ye yap1_t1r:
```env
FIREBASE_API_KEY=AIzaSyABCDEF123456...
```

---

## 2„ GOOGLE_OAUTH_CLIENT_ID (2 dakika)

### Ad1mlar:
1. Taray1c1da aÁ: https://console.cloud.google.com/apis/credentials?project=kamyonet-e3559
2. **"OAuth 2.0 Client IDs"** listesine bak

**Eer listede bir Web client varsa:**
- T1kla í Client ID'yi kopyala (`.apps.googleusercontent.com` ile biter)

**Eer liste bo_sa, yeni olu_tur:**
1. **"+ CREATE CREDENTIALS"** í **"OAuth client ID"**
2. **Application type**: Web application
3. **Name**: Nakliyenet Web
4. **Authorized redirect URIs** í **"+ ADD URI"**:
   ```
   https://nakliyenet.com/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   ```
5. **CREATE** t1kla
6. Popup'ta **Client ID**'yi kopyala

### ÷rnek:
```
123456789012-abcdefghijk.apps.googleusercontent.com
```

### .env'ye yap1_t1r:
```env
GOOGLE_OAUTH_CLIENT_ID=123456789012-abcdefghijk.apps.googleusercontent.com
```

---

## 3„ GOOGLE_OAUTH_CLIENT_SECRET (1 dakika)

### Ad1mlar:
1. Ayn1 sayfada: https://console.cloud.google.com/apis/credentials?project=kamyonet-e3559
2. **OAuth 2.0 Client ID**'ye t1kla (yukar1da olu_turduunuz)
3. **Client secret**'i kopyala (`GOCSPX-` ile ba_lar)

### ÷rnek:
```
GOCSPX-ABCxyz123_456
```

### .env'ye yap1_t1r:
```env
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-ABCxyz123_456
```

---

##  Bitti! ^imdi Test Et

### 1. Django'yu Ba_lat:
```bash
python manage.py runserver
```

### 2. Taray1c1da AÁ:
```
http://localhost:8000/giris/
```

### 3. "Google ile Giri_ Yap" Butonuna T1kla

**«al1_1yorsa:** Google hesab1 seÁme ekran1 aÁ1lmal1 

**«al1_m1yorsa:**
- Browser console (F12) í Hata mesaj1n1 kontrol et
- Django terminal í Hata mesaj1n1 kontrol et
- Bana hata mesaj1n1 gˆster

---

## =Ä Droplet'e Deploy (0stee Bal1)

Local'de test ettikten sonra, droplet'e deploy iÁin:

### 1. .env dosyas1n1 droplet'e kopyala:
```bash
scp .env root@164.90.215.249:/path/to/nakliyenet-django/
```

### 2. firebase-adminsdk.json'u kopyala:
```bash
scp firebase-adminsdk.json root@164.90.215.249:/path/to/nakliyenet-django/
```

### 3. Django admin'de SocialApp ekle:
```
https://nakliyenet.com/admin/
í Social applications í Add
í Provider: Google
í Client ID ve Secret: .env'deki deerleri yap1_t1r
í Sites: nakliyenet.com seÁin
í Save
```

### 4. Services'leri restart et:
```bash
ssh root@164.90.215.249
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## =  ÷zet

| Bilgi | Nereden | S¸re |
|-------|---------|------|
|  Firebase Project ID | Otomatik doldurdum | 0 dk |
|  Firebase Auth Domain | Otomatik doldurdum | 0 dk |
|  Firebase Storage Bucket | Otomatik doldurdum | 0 dk |
| =8 Firebase API Key | Firebase Console | 2 dk |
| =8 Google OAuth Client ID | Google Cloud Console | 2 dk |
| =8 Google OAuth Secret | Google Cloud Console | 1 dk |

**Toplam s¸re:** 5 dakika Ò

---

## =ﬁ Yard1m

Tak1l1rsan1z:
1. Ekran gˆr¸nt¸s¸ al1n
2. Hata mesaj1n1 kopyalay1n
3. Bana gˆnderin

**Ba_ar1lar!** =Ä
