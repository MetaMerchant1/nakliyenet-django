"""
Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from website.sitemaps import ShipmentSitemap, StaticViewSitemap
from website.admin import admin_site  # Import custom admin site

sitemaps = {
    'shipments': ShipmentSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin_site.urls),  # Use custom admin site
    path('api/v1/', include('website.api_urls')),  # REST API endpoints
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout
    path('accounts/', include('allauth.urls')),  # Google OAuth endpoints
    path('blog/', include('blog.urls')),  # Blog app
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
    path('', include('website.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
