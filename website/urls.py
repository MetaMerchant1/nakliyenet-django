"""
Website URL Configuration - SEO friendly URLs
"""
from django.urls import path
from . import views
from . import auth_views
from . import oauth_views
from . import sentry_test
from . import bid_views

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

    # Yasal sayfalar
    path('gizlilik-politikasi/', views.gizlilik_politikasi, name='gizlilik_politikasi'),
    path('kullanim-kosullari/', views.kullanim_kosullari, name='kullanim_kosullari'),

    # SEO - Şehir sayfaları
    path('nakliye/<str:sehir_slug>/', views.sehir_nakliye, name='sehir_nakliye'),

    # OAuth - Custom Google Login
    path('oauth/google/login/', oauth_views.google_login_start, name='google_login_start'),
    path('oauth/google/callback/', oauth_views.google_oauth_callback, name='google_oauth_callback'),
    path('oauth/google/debug/', oauth_views.google_login_debug, name='google_oauth_debug'),

    # Sentry Test Endpoints (production test - remove after verification)
    path('test-sentry-error/', sentry_test.sentry_test_error, name='test_sentry_error'),
    path('test-sentry-status/', sentry_test.sentry_test_success, name='test_sentry_status'),

    # Bid Management API
    path('teklif/<str:bid_id>/kabul/', bid_views.bid_accept, name='bid_accept'),
    path('teklif/<str:bid_id>/reddet/', bid_views.bid_reject, name='bid_reject'),
    path('teklif/<str:bid_id>/karsi-teklif/', bid_views.bid_counter_offer, name='bid_counter_offer'),
    path('teklif/<str:bid_id>/yorum/', bid_views.bid_comment, name='bid_comment'),
]
