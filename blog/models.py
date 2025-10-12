from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class BlogPost(models.Model):
    """Blog yazısı modeli - SEO için"""

    title = models.CharField('Başlık', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    content = models.TextField('İçerik')
    meta_description = models.CharField('Meta Açıklama', max_length=160, blank=True,
                                       help_text='SEO için kısa açıklama (max 160 karakter)')
    meta_keywords = models.CharField('Anahtar Kelimeler', max_length=200, blank=True,
                                    help_text='Virgülle ayrılmış anahtar kelimeler')

    # SEO ve yayın ayarları
    is_published = models.BooleanField('Yayında', default=True)
    featured_image = models.ImageField('Öne Çıkan Görsel', upload_to='blog/', blank=True, null=True)

    # Tarihler
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    published_at = models.DateTimeField('Yayın Tarihi', blank=True, null=True)

    # İstatistikler
    view_count = models.IntegerField('Görüntülenme', default=0)

    class Meta:
        verbose_name = 'Blog Yazısı'
        verbose_name_plural = 'Blog Yazıları'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Slug otomatik oluştur
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
