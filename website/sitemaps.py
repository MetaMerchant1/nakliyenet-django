"""
Sitemaps - Google için dinamik sitemap oluşturma
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from .models import Shipment


class ShipmentSitemap(Sitemap):
    """
    Aktif ilanlar için sitemap
    Google her ilan için ayrı URL indexler
    """
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        """Aktif ilanları getir"""
        return Shipment.objects.filter(
            status='active'
        ).order_by('-created_at')[:1000]

    def location(self, item):
        """Her ilan için URL"""
        return f'/ilan/{item.tracking_number}/'

    def lastmod(self, item):
        """Son değişiklik tarihi"""
        return item.updated_at or item.created_at


class StaticViewSitemap(Sitemap):
    """
    Statik sayfalar için sitemap
    """
    priority = 0.7
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return ['website:index', 'website:ilanlar', 'website:hakkimizda',
                'website:iletisim', 'website:nasil_calisir', 'website:sss',
                'website:gizlilik_politikasi', 'website:kullanim_kosullari']

    def location(self, item):
        return reverse(item)


class CitySitemap(Sitemap):
    """
    Şehir nakliye sayfaları için sitemap - SEO için önemli
    """
    priority = 0.8
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        """Popüler şehirler için URL'ler"""
        return [
            'istanbul', 'ankara', 'izmir', 'bursa', 'antalya',
            'adana', 'gaziantep', 'konya', 'mersin', 'kayseri',
            'eskisehir', 'diyarbakir', 'samsun', 'denizli', 'sanliurfa',
            'gebze', 'kocaeli', 'darica', 'adapazari', 'tekirdag',
            'balikesir', 'aydin', 'manisa', 'trabzon', 'sakarya',
        ]

    def location(self, item):
        return f'/nakliye/{item}/'
