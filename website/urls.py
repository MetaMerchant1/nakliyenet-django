"""
Website URL Configuration - SEO friendly URLs
"""
from django.urls import path
from . import views
from . import auth_views

app_name = 'website'

urlpatterns = [
    # Ana sayfa
    path('', views.index, name='index'),

    # İlanlar
    path('ilanlar/', views.ilan_listesi, name='ilanlar'),
    path('ilan-olustur/', views.ilan_olustur, name='ilan_olustur'),
    path('ilan/<str:tracking_number>/', views.ilan_detay, name='ilan_detay'),
    path('ilan/<str:tracking_number>/teklif-ver/', views.teklif_ver, name='teklif_ver'),

    # İlanlarım - Kullanıcının ilanları
    path('ilanlarim/', views.ilanlarim, name='ilanlarim'),
    path('teklif/<str:bid_id>/kabul-et/', views.teklif_kabul_et, name='teklif_kabul_et'),
    path('teklif/<str:bid_id>/reddet/', views.teklif_reddet, name='teklif_reddet'),

    # Ödeme ve Teslim
    path('odeme/<str:payment_id>/', views.odeme_yap, name='odeme_yap'),
    path('teslim-onayla/<str:payment_id>/', views.teslim_onayla, name='teslim_onayla'),

    # Authentication
    path('giris/', auth_views.login_view, name='login'),
    path('kayit/', auth_views.register_view, name='register'),
    path('cikis/', auth_views.logout_view, name='logout'),
    path('profilim/', views.profil, name='profil'),
    path('belge-yukle/', views.belge_yukle, name='belge_yukle'),

    # API endpoints for authentication
    path('api/check-email/', auth_views.api_check_email, name='api_check_email'),

    # Statik sayfalar
    path('hakkimizda/', views.hakkimizda, name='hakkimizda'),
    path('iletisim/', views.iletisim, name='iletisim'),
    path('nasil-calisir/', views.nasil_calisir, name='nasil_calisir'),
    path('sss/', views.sss, name='sss'),
]
