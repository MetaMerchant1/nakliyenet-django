"""
Management command to create sample SEO-optimized blog posts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Create sample SEO-optimized blog posts'

    def handle(self, *args, **options):
        sample_posts = [
            {
                'title': "İstanbul'da Evden Eve Nakliye Fiyatları 2025 - Uygun Fiyatlı Taşıma",
                'meta_keywords': 'istanbul nakliye, evden eve nakliye, nakliye fiyatları, istanbul taşımacılık',
                'content': """
<h2>İstanbul'da Evden Eve Nakliye Fiyatları 2025</h2>

<p>İstanbul'da evden eve nakliye fiyatları 2025 yılında metrekare, mesafe ve eşya miktarına göre değişiklik göstermektedir. NAKLIYE NET platformu ile en uygun fiyatlı nakliye hizmeti alabileceğiniz taşıyıcıları karşılaştırabilirsiniz.</p>

<h3>2025 Ortalama Nakliye Fiyatları</h3>
<ul>
    <li><strong>1+1 Daire:</strong> 3.000 - 5.000 TL</li>
    <li><strong>2+1 Daire:</strong> 5.000 - 8.000 TL</li>
    <li><strong>3+1 Daire:</strong> 8.000 - 12.000 TL</li>
    <li><strong>4+1 ve üzeri:</strong> 12.000 TL ve üzeri</li>
</ul>

<h3>Fiyatı Etkileyen Faktörler</h3>
<p>İstanbul'da nakliye fiyatlarını etkileyen başlıca faktörler:</p>
<ol>
    <li><strong>Taşınacak Metrekare:</strong> Ev büyüdükçe fiyat artar</li>
    <li><strong>Mesafe:</strong> İlçeler arası mesafe önemli</li>
    <li><strong>Kat Sayısı:</strong> Asansörlü/asansörsüz fark yaratır</li>
    <li><strong>Eşya Miktarı:</strong> Beyaz eşya ve mobilya sayısı</li>
    <li><strong>Sezon:</strong> Yaz ayları daha yoğun ve pahalı</li>
    <li><strong>Sigorta:</strong> Nakliye sigortası ek maliyet</li>
</ol>

<h3>NAKLIYE NET ile Tasarruf Edin</h3>
<p>NAKLIYE NET platformu ile nakliye maliyetlerinizi %30'a kadar düşürebilirsiniz:</p>
<ul>
    <li>Birden fazla taşıyıcıdan teklif alın</li>
    <li>Fiyatları karşılaştırın</li>
    <li>Kullanıcı yorumlarını okuyun</li>
    <li>Doğrulanmış taşıyıcılarla çalışın</li>
    <li>Güvenli ödeme sistemi</li>
</ul>

<h3>İstanbul'un Popüler İlçelerinde Nakliye</h3>
<p>İstanbul'un farklı ilçelerinde nakliye hizmeti veriyoruz:</p>
<ul>
    <li>Kadıköy - Kartal - Maltepe</li>
    <li>Üsküdar - Ümraniye - Ataşehir</li>
    <li>Şişli - Beşiktaş - Beyoğlu</li>
    <li>Bakırköy - Küçükçekmece - Avcılar</li>
    <li>Pendik - Tuzla - Gebze arası</li>
</ul>

<h3>Hemen Teklif Alın</h3>
<p>NAKLIYE NET'e ücretsiz kayıt olun, ilanınızı oluşturun ve dakikalar içinde doğrulanmış taşıyıcılardan teklif almaya başlayın. Güvenli, hızlı ve ekonomik nakliye için hemen başvurun!</p>

<p><strong>Not:</strong> Tüm fiyatlar ortalama değerlerdir. Kesin fiyat için NAKLIYE NET üzerinden teklif almanızı öneririz.</p>
""",
                'meta_description': "İstanbul evden eve nakliye fiyatları 2025. Uygun fiyatlı taşıma hizmeti için NAKLIYE NET'ten teklif alın. %30 tasarruf fırsatı!",
                'status': 'published',
            },
            {
                'title': "Nakliye Yaparken Nelere Dikkat Edilmeli? 10 Önemli İpucu",
                'meta_keywords': 'nakliye ipuçları, evden eve nakliye, nakliye tavsiyeleri, güvenli taşıma',
                'content': """
<h2>Nakliye Yaparken Nelere Dikkat Edilmeli?</h2>

<p>Evden eve nakliye yaparken doğru hazırlık ve planlama çok önemlidir. İşte başarılı bir taşınma için 10 önemli ipucu:</p>

<h3>1. Önceden Planlama Yapın</h3>
<p>Taşınma tarihinden en az 2-3 hafta önce planlamaya başlayın. NAKLIYE NET üzerinden erken rezervasyon yaparak daha uygun fiyatlar elde edebilirsiniz.</p>

<h3>2. Doğru Nakliye Firması Seçin</h3>
<p>NAKLIYE NET platformunda:</p>
<ul>
    <li>Belgesi doğrulanmış taşıyıcılar</li>
    <li>Gerçek kullanıcı yorumları</li>
    <li>Puanlama sistemi</li>
    <li>Geçmiş iş performansı</li>
</ul>

<h3>3. Eşyalarınızı Kategorize Edin</h3>
<p>Taşınmadan önce eşyalarınızı gruplandırın:</p>
<ul>
    <li>Kırılabilir eşyalar</li>
    <li>Değerli eşyalar</li>
    <li>Beyaz eşyalar</li>
    <li>Kitaplar ve dokümanlar</li>
    <li>Giysi ve tekstil</li>
</ul>

<h3>4. Kaliteli Ambalaj Malzemesi Kullanın</h3>
<p>Eşyalarınızın zarar görmemesi için:</p>
<ul>
    <li>Sağlam karton kutular</li>
    <li>Balonlu naylon</li>
    <li>Streç film</li>
    <li>Köşe koruyucular</li>
</ul>

<h3>5. Sigorta Yaptırın</h3>
<p>Değerli eşyalarınız için nakliye sigortası yaptırmayı unutmayın. NAKLIYE NET ile çalışan taşıyıcılar sigorta seçeneği sunmaktadır.</p>

<h3>6. Envanter Listesi Hazırlayın</h3>
<p>Tüm eşyalarınızın listesini çıkarın ve fotoğraflayın. Bu, olası kayıp veya hasar durumunda size yardımcı olur.</p>

<h3>7. Kırılabilir Eşyaları Özel Paketleyin</h3>
<p>Cam, porselen ve elektronik eşyalarınızı ekstra koruma ile paketleyin ve kutular üzerine "KIRILIR" işareti koyun.</p>

<h3>8. Önemli Eşyaları Kendiniz Taşıyın</h3>
<p>Kişisel belgeler, değerli takılar ve önemli dökümanları kendiniz taşıyın.</p>

<h3>9. Eski ve Yeni Evin Hazırlığını Yapın</h3>
<p>Her iki evde de:</p>
<ul>
    <li>Asansör rezervasyonu yapın</li>
    <li>Giriş/çıkış yollarını açık tutun</li>
    <li>Gerekli izinleri alın</li>
</ul>

<h3>10. Taşıyıcı ile İletişimde Kalın</h3>
<p>NAKLIYE NET'in mesajlaşma sistemi ile taşıyıcınızla sürekli iletişimde kalın. Konum takibi yaparak yükünüzü gerçek zamanlı izleyin.</p>

<h3>Sonuç</h3>
<p>Bu ipuçlarını uygulayarak sorunsuz bir nakliye deneyimi yaşayabilirsiniz. NAKLIYE NET ile güvenli ve ekonomik taşımacılık!</p>
""",
                'meta_description': "Nakliye yaparken dikkat edilmesi gereken 10 önemli ipucu. Eşyalarınızı güvenle taşımak için bu tavsiyeleri mutlaka okuyun!",
                'status': 'published',
            },
            {
                'title': "Ankara'da Ofis Taşıma - Profesyonel Kurumsal Nakliye Hizmeti",
                'meta_keywords': 'ankara ofis taşıma, kurumsal nakliye, ankara nakliye, ofis nakliyesi',
                'content': """
<h2>Ankara'da Profesyonel Ofis Taşıma Hizmeti</h2>

<p>Ankara'da ofis taşıma işi profesyonel bir ekip ve dikkatli planlama gerektirir. NAKLIYE NET ile kurumsal nakliye hizmetlerinde uzman taşıyıcılardan teklif alabilirsiniz.</p>

<h3>Ofis Taşımada Farklılıklar</h3>
<p>Ofis taşıma, ev taşımadan farklı özellikler gerektirir:</p>
<ul>
    <li>Hassas ofis ekipmanları (bilgisayar, yazıcı)</li>
    <li>Kurumsal dosya ve arşivler</li>
    <li>Büyük ofis mobilyaları</li>
    <li>Minimum iş kesintisi</li>
    <li>Güvenlik ve gizlilik</li>
</ul>

<h3>Ankara Ofis Taşıma Fiyatları</h3>
<p>2025 Ankara ofis taşıma fiyatları:</p>
<ul>
    <li><strong>Küçük Ofis (10-20 kişi):</strong> 8.000 - 15.000 TL</li>
    <li><strong>Orta Ofis (20-50 kişi):</strong> 15.000 - 30.000 TL</li>
    <li><strong>Büyük Ofis (50+ kişi):</strong> 30.000 TL ve üzeri</li>
</ul>

<h3>Ofis Taşıma Süreci</h3>
<p>NAKLIYE NET ile ofis taşıma adımları:</p>
<ol>
    <li><strong>Keşif ve Planlama:</strong> Mevcut ofisi inceleme</li>
    <li><strong>Teklif Alma:</strong> Birden fazla taşıyıcıdan fiyat teklifi</li>
    <li><strong>Tarih Belirleme:</strong> İş akışını etkilemeyecek zaman seçimi</li>
    <li><strong>Paketleme:</strong> Profesyonel ambalaj hizmeti</li>
    <li><strong>Taşıma:</strong> Güvenli ve hızlı taşıma</li>
    <li><strong>Kurulum:</strong> Yeni ofiste yerleştirme</li>
</ol>

<h3>Ankara'da Popüler Ofis Bölgeleri</h3>
<p>Ankara'nın öne çıkan iş merkezleri:</p>
<ul>
    <li>Çankaya - Kızılay</li>
    <li>Söğütözü - Konutkent</li>
    <li>Ümitköy - Beytepe</li>
    <li>Bilkent - Çayyolu</li>
    <li>Ostim OSB</li>
</ul>

<h3>Neden NAKLIYE NET?</h3>
<ul>
    <li>Kurumsal nakliye deneyimi olan taşıyıcılar</li>
    <li>Sigortali taşıma seçenekleri</li>
    <li>Hafta sonu ve mesai dışı taşıma</li>
    <li>IT ekipman taşıma uzmanlığı</li>
    <li>Şeffaf fiyatlandırma</li>
</ul>

<h3>Hemen Teklif Alın</h3>
<p>Ankara'da ofis taşıma için NAKLIYE NET'e ücretsiz kayıt olun. Kurumsal nakliye konusunda deneyimli taşıyıcılardan anında teklif alın!</p>
""",
                'meta_description': "Ankara ofis taşıma hizmeti. Profesyonel kurumsal nakliye için NAKLIYE NET'ten teklif alın. Güvenli ve hızlı taşıma!",
                'status': 'published',
            },
        ]

        created_count = 0
        for post_data in sample_posts:
            # Check if post already exists
            if not BlogPost.objects.filter(title=post_data['title']).exists():
                post_data['published_at'] = timezone.now()
                post_data['is_published'] = True
                BlogPost.objects.create(**post_data)
                created_count += 1
                print(f'[OK] Created blog post')
            else:
                print(f'[SKIP] Blog post already exists')

        print(f'\nSuccessfully created {created_count} blog posts!')
        print(f'Total blog posts in database: {BlogPost.objects.count()}')
