# SEO Setup Guide - NAKLIYE NET

## 📋 Yapılacaklar Listesi

### 1. Google Search Console

**Adımlar:**
1. https://search.google.com/search-console/ adresine gidin
2. "Mülk Ekle" > "Alan Adı" seçin
3. `nakliyenet.com` girin
4. Doğrulama kodunu alın
5. `templates/base.html` dosyasında `YOUR_VERIFICATION_CODE_HERE` yerine koyun
6. Deploy edin
7. Doğrulamayı tamamlayın
8. "Sitemap Gönder" > `https://nakliyenet.com/sitemap.xml` ekleyin

**Sitemap URL:** https://nakliyenet.com/sitemap.xml
**Robots.txt URL:** https://nakliyenet.com/robots.txt

### 2. Google Analytics 4

**Adımlar:**
1. https://analytics.google.com/ adresine gidin
2. Yeni "Mülk" oluşturun
3. "Veri Akışı" > "Web" seçin
4. `nakliyenet.com` girin
5. Measurement ID'yi (`G-XXXXXXXXXX`) alın
6. `templates/base.html` dosyasında 2 yerde değiştirin (satır 116 ve 121)
7. Deploy edin

**Tracking Özellikleri:**
- Sayfa görüntülemeleri (otomatik)
- İlan görüntülemeleri (`trackShipmentView` fonksiyonu)
- Teklif gönderileri (`trackBidSubmit` fonksiyonu)

### 3. Google My Business

**Adımlar:**
1. https://business.google.com/ adresine gidin
2. İşletme ekleyin
3. Kategori: "Nakliye Şirketi" veya "Taşımacılık Hizmeti"
4. Adres, telefon, web sitesi ekleyin
5. Çalışma saatlerini belirtin
6. Doğrulama için posta kartı/telefon seçin

### 4. Yandex Webmaster

**Adımlar:**
1. https://webmaster.yandex.com/ adresine gidin
2. Site ekleyin: `nakliyenet.com`
3. Doğrulama yap
4. Sitemap ekleyin: `https://nakliyenet.com/sitemap.xml`

### 5. Bing Webmaster Tools

**Adımlar:**
1. https://www.bing.com/webmasters adresine gidin
2. Site ekleyin
3. Google Search Console verilerini import edebilirsiniz
4. Sitemap ekleyin

## 🎯 SEO Best Practices

### Meta Tags
- ✅ Title tags (her sayfada unique)
- ✅ Meta descriptions (155 karakter)
- ✅ Canonical URLs
- ✅ Open Graph tags
- ✅ Twitter Cards

### Technical SEO
- ✅ Sitemap.xml (otomatik güncellenen)
- ✅ Robots.txt
- ✅ Mobile responsive
- ✅ HTTPS
- ✅ Page speed optimization
- ✅ Structured data (Schema.org)

### Content SEO
- 📝 TODO: Blog bölümü ekle
- 📝 TODO: Şehir bazlı landing pages
- 📝 TODO: FAQPage schema ekle
- 📝 TODO: User reviews/ratings

### Off-Page SEO
- 📝 TODO: Sosyal medya profilleri
- 📝 TODO: Yerel dizinlere kayıt
- 📝 TODO: Backlink stratejisi

## 📊 Monitoring

### Google Search Console
- Indexlenen sayfalar
- Arama performansı
- Hata raporları
- Mobile usability

### Google Analytics
- Trafik kaynakları
- Kullanıcı davranışları
- Conversion tracking
- Bounce rate

## 🚀 İlk 30 Günde Yapılacaklar

### Hafta 1
- [x] robots.txt oluştur
- [x] Google Analytics ekle
- [ ] Google Search Console doğrulama
- [ ] Sitemap gönder

### Hafta 2
- [ ] Google My Business kaydı
- [ ] Yandex Webmaster Tools
- [ ] Bing Webmaster Tools
- [ ] İlk analytics raporlarını incele

### Hafta 3
- [ ] Blog bölümü oluştur
- [ ] İlk 5 blog yazısı
- [ ] Şehir sayfaları (İstanbul, Ankara, İzmir)
- [ ] FAQPage schema ekle

### Hafta 4
- [ ] Sosyal medya profilleri (LinkedIn, Facebook, Instagram)
- [ ] Yerel dizinlere kayıt (Sahibinden, Yandex Haritalar)
- [ ] Google Business Profile optimize et
- [ ] İlk aylık SEO raporu

## 💡 Pro Tips

1. **İçerik Düzenli Olmalı:** Haftada en az 1-2 blog yazısı
2. **Long-tail Keywords:** "İstanbul Ankara arası nakliye fiyatları"
3. **Local SEO:** Şehir + hizmet kombinasyonları
4. **User Generated Content:** Müşteri yorumları ve rating'ler
5. **Internal Linking:** İlanlar arası bağlantılar
6. **Image Optimization:** Alt text ve dosya isimleri
7. **Loading Speed:** Minimize CSS/JS, optimize images
8. **Mobile First:** Mobil optimizasyona öncelik

## 📞 Destek

Sorularınız için:
- Email: seo@nakliyenet.com
- Google Search Console yardım: https://support.google.com/webmasters
- Google Analytics yardım: https://support.google.com/analytics
