# -*- coding: utf-8 -*-
"""
Custom Admin Dashboard with Statistics
"""
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Shipment, Bid, UserProfile, Vehicle


class AdminDashboard:
    """Admin dashboard with statistics"""

    @staticmethod
    def get_dashboard_stats():
        """Get comprehensive statistics for dashboard"""
        today = timezone.now()
        last_7_days = today - timedelta(days=7)

        # Shipment statistics
        total_shipments = Shipment.objects.count()
        active_shipments = Shipment.objects.filter(status='active').count()
        completed_shipments = Shipment.objects.filter(status='completed').count()
        shipments_last_7_days = Shipment.objects.filter(created_at__gte=last_7_days).count()

        # Bid statistics
        total_bids = Bid.objects.count()
        pending_bids = Bid.objects.filter(status='pending').count()
        accepted_bids = Bid.objects.filter(status='accepted').count()

        # User statistics
        total_users = UserProfile.objects.count()
        total_carriers = UserProfile.objects.filter(user_type=1).count()
        verified_carriers = UserProfile.objects.filter(user_type=1, documents_verified=True).count()

        # Financial statistics
        total_suggested_value = Shipment.objects.aggregate(total=Sum('suggested_price'))['total'] or 0
        total_final_value = Shipment.objects.filter(final_price__isnull=False).aggregate(total=Sum('final_price'))['total'] or 0

        return {
            'shipments': {
                'total': total_shipments,
                'active': active_shipments,
                'completed': completed_shipments,
                'last_7_days': shipments_last_7_days,
            },
            'bids': {
                'total': total_bids,
                'pending': pending_bids,
                'accepted': accepted_bids,
            },
            'users': {
                'total': total_users,
                'carriers': total_carriers,
                'verified_carriers': verified_carriers,
            },
            'financial': {
                'total_suggested': total_suggested_value,
                'total_final': total_final_value,
            },
        }

    @staticmethod
    def render_dashboard_html(stats):
        """Render dashboard HTML"""
        html = f"""
        <div style="padding: 20px; background: #f8f9fa;">
            <h1 style="color: #2c3e50; margin-bottom: 30px;">NAKLIYE NET - Istatistikler</h1>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3498db;">
                    <div style="font-size: 14px; color: #7f8c8d;">TOPLAM ILAN</div>
                    <div style="font-size: 32px; font-weight: bold; color: #2c3e50; margin: 10px 0;">{stats['shipments']['total']}</div>
                    <div style="font-size: 12px; color: #27ae60;">+{stats['shipments']['last_7_days']} son 7 gunde</div>
                </div>

                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #27ae60;">
                    <div style="font-size: 14px; color: #7f8c8d;">AKTIF ILANLAR</div>
                    <div style="font-size: 32px; font-weight: bold; color: #2c3e50; margin: 10px 0;">{stats['shipments']['active']}</div>
                </div>

                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #f39c12;">
                    <div style="font-size: 14px; color: #7f8c8d;">BEKLEYEN TEKLIFLER</div>
                    <div style="font-size: 32px; font-weight: bold; color: #2c3e50; margin: 10px 0;">{stats['bids']['pending']}</div>
                </div>

                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #27ae60;">
                    <div style="font-size: 14px; color: #7f8c8d;">ONAYLI TASIYICILAR</div>
                    <div style="font-size: 32px; font-weight: bold; color: #2c3e50; margin: 10px 0;">{stats['users']['verified_carriers']}</div>
                </div>

                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3498db;">
                    <div style="font-size: 14px; color: #7f8c8d;">TOPLAM ILAN DEGERI</div>
                    <div style="font-size: 32px; font-weight: bold; color: #2c3e50; margin: 10px 0;">{stats['financial']['total_suggested']:,.0f} TL</div>
                </div>

                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #27ae60;">
                    <div style="font-size: 14px; color: #7f8c8d;">KESINLESEN DEGER</div>
                    <div style="font-size: 32px; font-weight: bold; color: #2c3e50; margin: 10px 0;">{stats['financial']['total_final']:,.0f} TL</div>
                </div>
            </div>

            <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Hizli Islemler</h2>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <a href="/admin/website/shipment/" style="display: inline-block; padding: 12px 24px; background: #3498db; color: white; text-decoration: none; border-radius: 4px;">Tum Ilanlar</a>
                    <a href="/admin/website/bid/" style="display: inline-block; padding: 12px 24px; background: #f39c12; color: white; text-decoration: none; border-radius: 4px;">Tum Teklifler</a>
                    <a href="/admin/website/userprofile/" style="display: inline-block; padding: 12px 24px; background: #27ae60; color: white; text-decoration: none; border-radius: 4px;">Kullanicilar</a>
                    <a href="/admin/website/vehicle/" style="display: inline-block; padding: 12px 24px; background: #9b59b6; color: white; text-decoration: none; border-radius: 4px;">Araclar</a>
                </div>
            </div>
        </div>
        """
        return format_html(html)
