from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'is_published', 'view_count', 'created_at']
    list_filter = ['status', 'is_published', 'created_at']
    search_fields = ['title', 'content', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    actions = ['publish_posts', 'draft_posts']

    fieldsets = (
        ('İçerik', {
            'fields': ('title', 'slug', 'content', 'featured_image')
        }),
        ('SEO Ayarları', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Yayın Ayarları', {
            'fields': ('status', 'is_published', 'published_at')
        }),
        ('İstatistikler', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['view_count']

    def publish_posts(self, request, queryset):
        """Seçili blog yazılarını yayınla"""
        updated = queryset.update(status='published', is_published=True, published_at=timezone.now())
        self.message_user(request, f'{updated} blog yazısı yayınlandı.')
    publish_posts.short_description = 'Seçili yazıları yayınla'

    def draft_posts(self, request, queryset):
        """Seçili blog yazılarını taslağa al"""
        updated = queryset.update(status='draft', is_published=False)
        self.message_user(request, f'{updated} blog yazısı taslağa alındı.')
    draft_posts.short_description = 'Seçili yazıları taslağa al'

    def get_urls(self):
        """Admin panel için özel URL'ler"""
        urls = super().get_urls()
        custom_urls = [
            path('blog-olusturucu/', self.admin_site.admin_view(self.blog_generator_view), name='blog-generator'),
        ]
        return custom_urls + urls

    def blog_generator_view(self, request):
        """Blog oluşturucu sayfası"""
        if request.method == 'POST':
            # Blog yazısı oluştur
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            content_type = request.POST.get('content_type', 'guide')

            if title:
                # SEO-optimized content templates
                content_templates = {
                    'guide': self._generate_guide_content(title, keywords),
                    'tips': self._generate_tips_content(title, keywords),
                    'comparison': self._generate_comparison_content(title, keywords),
                }

                content = content_templates.get(content_type, content_templates['guide'])

                # Meta description oluştur
                meta_desc = f"{title[:150]}..." if len(title) > 150 else title

                # Blog yazısı kaydet
                post = BlogPost.objects.create(
                    title=title,
                    content=content,
                    meta_description=meta_desc,
                    meta_keywords=keywords or '',
                    status='draft',
                    is_published=False,
                )

                messages.success(request, f'Blog yazısı "{title}" taslak olarak oluşturuldu. Düzenleyip yayınlayabilirsiniz.')
                return redirect('admin:blog_blogpost_change', post.id)

        context = {
            'title': 'Blog Yazısı Oluşturucu',
            'site_title': 'NAKLIYE NET Admin',
            'has_permission': True,
        }
        return render(request, 'admin/blog/blog_generator.html', context)

    def _generate_guide_content(self, title, keywords):
        """Rehber tipi içerik şablonu"""
        return f"""
<h2>{title}</h2>

<p>Nakliye sektöründe {keywords or 'profesyonel hizmet'} almak isteyenler için hazırladığımız bu rehberde, bilinmesi gereken tüm detayları bulabilirsiniz.</p>

<h3>Giriş</h3>
<p>NAKLIYE NET olarak, müşterilerimize en iyi hizmeti sunmak için sürekli kendimizi geliştiriyoruz. Bu yazıda sizler için {title.lower()} hakkında kapsamlı bir rehber hazırladık.</p>

<h3>Neden Önemli?</h3>
<ul>
    <li>Güvenli ve hızlı taşımacılık</li>
    <li>Doğrulanmış taşıyıcılar</li>
    <li>Rekabetçi fiyatlar</li>
    <li>7/24 destek hizmeti</li>
</ul>

<h3>Nasıl Çalışır?</h3>
<ol>
    <li><strong>İlan Oluşturun:</strong> Web sitemizden ücretsiz kayıt olun ve yük ilanınızı oluşturun.</li>
    <li><strong>Teklif Alın:</strong> Doğrulanmış taşıyıcılardan anında teklif alın ve karşılaştırın.</li>
    <li><strong>Taşıyıcı Seçin:</strong> Size en uygun teklifi veren taşıyıcıyı seçin.</li>
    <li><strong>Güvenle Taşıyın:</strong> Escrow ödeme sistemi ile paranız güvende, yükünüzü takip edin.</li>
</ol>

<h3>Önemli İpuçları</h3>
<p>Nakliye hizmeti alırken dikkat edilmesi gereken önemli noktalar:</p>
<ul>
    <li>Taşıyıcının belgelerinin doğrulanmış olduğundan emin olun</li>
    <li>Kullanıcı yorumlarını okuyun</li>
    <li>Fiyat karşılaştırması yapın</li>
    <li>Sigorta seçeneklerini değerlendirin</li>
</ul>

<h3>NAKLIYE NET Farkı</h3>
<p>NAKLIYE NET ile nakliye işlemlerinizi güvenle gerçekleştirebilirsiniz. Platformumuzda:</p>
<ul>
    <li>Tüm taşıyıcılar belge kontrolünden geçer</li>
    <li>Escrow ödeme sistemi ile paranız güvende</li>
    <li>Gerçek zamanlı takip sistemi</li>
    <li>7/24 müşteri desteği</li>
</ul>

<h3>Sonuç</h3>
<p>NAKLIYE NET ile {keywords or 'nakliye hizmeti'} almak artık çok kolay. Hemen kayıt olun ve güvenli taşımacılığın keyfini çıkarın!</p>

<p><strong>İletişim:</strong> Daha fazla bilgi için <a href="/">web sitemizi</a> ziyaret edebilir veya müşteri hizmetlerimizle iletişime geçebilirsiniz.</p>
"""

    def _generate_tips_content(self, title, keywords):
        """İpuçları tipi içerik şablonu"""
        return f"""
<h2>{title}</h2>

<p>{keywords or 'Nakliye'} konusunda size yardımcı olacak önemli ipuçları ve öneriler.</p>

<h3>1. Planlama Yapın</h3>
<p>Nakliye işlemlerinizi önceden planlayarak hem zaman hem de maliyet tasarrufu sağlayabilirsiniz.</p>

<h3>2. Doğru Taşıyıcı Seçin</h3>
<p>NAKLIYE NET platformunda doğrulanmış taşıyıcılar arasından size en uygun olanı seçin. Kullanıcı yorumlarını mutlaka inceleyin.</p>

<h3>3. Fiyat Karşılaştırması Yapın</h3>
<p>Birden fazla taşıyıcıdan teklif alarak en uygun fiyatı bulun. NAKLIYE NET ile %30'a kadar tasarruf edebilirsiniz.</p>

<h3>4. Eşyalarınızı Sigortalayın</h3>
<p>Değerli eşyalarınız için sigorta yaptırmayı unutmayın. Bu size ekstra güvenlik sağlar.</p>

<h3>5. İletişimde Kalın</h3>
<p>Taşıyıcınızla düzenli iletişim halinde olun. NAKLIYE NET'in mesajlaşma sistemi ile kolayca iletişim kurabilirsiniz.</p>

<h3>Sonuç</h3>
<p>Bu ipuçlarını uygulayarak nakliye işleminizi sorunsuz bir şekilde tamamlayabilirsiniz. NAKLIYE NET ile güvenli taşımacılık!</p>
"""

    def _generate_comparison_content(self, title, keywords):
        """Karşılaştırma tipi içerik şablonu"""
        return f"""
<h2>{title}</h2>

<p>{keywords or 'Nakliye seçenekleri'} arasında karşılaştırma yaparak en iyi kararı vermenize yardımcı oluyoruz.</p>

<h3>Geleneksel Nakliye vs NAKLIYE NET</h3>

<h4>Geleneksel Nakliye</h4>
<ul>
    <li>Telefon ile arama yapmanız gerekir</li>
    <li>Tek bir firmadan teklif alırsınız</li>
    <li>Fiyat karşılaştırması zor</li>
    <li>Taşıyıcı güvenilirliği belirsiz</li>
</ul>

<h4>NAKLIYE NET ile Dijital Nakliye</h4>
<ul>
    <li>Online ilan oluşturma - 5 dakikada tamamlanır</li>
    <li>Birden fazla taşıyıcıdan otomatik teklif</li>
    <li>Kolay fiyat karşılaştırması</li>
    <li>Doğrulanmış taşıyıcılar</li>
    <li>Kullanıcı yorumları ve puanlama sistemi</li>
    <li>Escrow ödeme güvencesi</li>
    <li>Gerçek zamanlı takip</li>
</ul>

<h3>Sonuç</h3>
<p>NAKLIYE NET ile nakliye işlemlerinizi modern, güvenli ve ekonomik bir şekilde gerçekleştirin. Hemen kayıt olun!</p>
"""
