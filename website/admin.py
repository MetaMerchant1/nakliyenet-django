"""
Django Admin Configuration for NAKLIYE NET
Admin panel for document verification, shipment approvals, and monitoring
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Q
from .models import UserDocument, AdminActivity, UserProfile, Bid, Vehicle, Shipment, Payment


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    """Admin interface for user document verification"""

    list_display = [
        'user_email',
        'document_type_badge',
        'status_badge',
        'uploaded_at',
        'verified_by',
        'document_preview'
    ]

    list_filter = [
        'status',
        'document_type',
        'uploaded_at',
        'verified_at',
    ]

    search_fields = [
        'user_email',
        'user_name',
    ]

    readonly_fields = [
        'user_email',
        'user_name',
        'document_url',
        'uploaded_at',
        'document_image_preview',
    ]

    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user_email', 'user_name')
        }),
        ('Belge Bilgileri', {
            'fields': ('document_type', 'document_url', 'document_image_preview', 'uploaded_at')
        }),
        ('Onay Durumu', {
            'fields': ('status', 'verified_at', 'verified_by')
        }),
        ('Notlar', {
            'fields': ('rejection_reason', 'notes'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_documents', 'reject_documents']

    def document_type_badge(self, obj):
        """Display document type with badge"""
        colors = {
            'license': '#3498db',
            'registration': '#2ecc71',
            'src': '#9b59b6',
            'psychotech': '#e74c3c',
        }
        color = colors.get(obj.document_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_document_type_display()
        )
    document_type_badge.short_description = 'Belge Türü'

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#f39c12',
            'approved': '#27ae60',
            'rejected': '#c0392b',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'

    def document_preview(self, obj):
        """Show preview link"""
        return format_html(
            '<a href="{}" target="_blank" style="color: #3498db;">Görüntüle</a>',
            obj.document_url
        )
    document_preview.short_description = 'Belge'

    def document_image_preview(self, obj):
        """Show full image preview in detail view"""
        if obj.document_url:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 800px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;"/>',
                obj.document_url
            )
        return "Belge yok"
    document_image_preview.short_description = 'Belge Önizleme'

    def approve_documents(self, request, queryset):
        """Bulk approve documents"""
        count = 0
        for doc in queryset.filter(status='pending'):
            doc.status = 'approved'
            doc.verified_at = timezone.now()
            doc.verified_by = request.user
            doc.save()

            # Log activity
            AdminActivity.objects.create(
                admin_user=request.user,
                action_type='document_approved',
                target_type='document',
                target_id=str(doc.id),
                description=f"{doc.get_document_type_display()} onaylandı - {doc.user_email}",
                ip_address=self.get_client_ip(request)
            )
            count += 1

        self.message_user(request, f"✅ {count} belge başarıyla onaylandı!", 'success')
    approve_documents.short_description = "✅ Seçili belgeleri ONAYLA"

    def reject_documents(self, request, queryset):
        """Bulk reject documents"""
        count = 0
        for doc in queryset.filter(status='pending'):
            doc.status = 'rejected'
            doc.verified_at = timezone.now()
            doc.verified_by = request.user
            doc.save()

            # Log activity
            AdminActivity.objects.create(
                admin_user=request.user,
                action_type='document_rejected',
                target_type='document',
                target_id=str(doc.id),
                description=f"{doc.get_document_type_display()} reddedildi - {doc.user_email}",
                ip_address=self.get_client_ip(request)
            )
            count += 1

        self.message_user(request, f"❌ {count} belge reddedildi.", level='warning')
    reject_documents.short_description = "❌ Seçili belgeleri REDDET"

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def save_model(self, request, obj, form, change):
        """Auto-set verified_by when status changes"""
        if change:  # Editing existing object
            old_obj = UserDocument.objects.get(pk=obj.pk)
            if old_obj.status != obj.status and obj.status in ['approved', 'rejected']:
                obj.verified_by = request.user
                obj.verified_at = timezone.now()

                # Log activity
                action_type = 'document_approved' if obj.status == 'approved' else 'document_rejected'
                AdminActivity.objects.create(
                    admin_user=request.user,
                    action_type=action_type,
                    target_type='document',
                    target_id=str(obj.id),
                    description=f"{obj.get_document_type_display()} {obj.get_status_display()} - {obj.user_email}",
                    ip_address=self.get_client_ip(request)
                )

        super().save_model(request, obj, form, change)


@admin.register(AdminActivity)
class AdminActivityAdmin(admin.ModelAdmin):
    """Admin interface for activity log"""

    list_display = [
        'timestamp',
        'admin_user',
        'action_type_badge',
        'description_short',
        'target_type',
        'ip_address',
    ]

    list_filter = [
        'action_type',
        'target_type',
        'timestamp',
        'admin_user',
    ]

    search_fields = [
        'description',
        'target_id',
        'admin_user__username',
        'admin_user__email',
    ]

    readonly_fields = [
        'admin_user',
        'action_type',
        'target_type',
        'target_id',
        'description',
        'timestamp',
        'ip_address',
    ]

    def has_add_permission(self, request):
        """Prevent manual creation of activity logs"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of activity logs"""
        return False

    def action_type_badge(self, obj):
        """Display action type with colored badge"""
        colors = {
            'document_approved': '#27ae60',
            'document_rejected': '#c0392b',
            'shipment_approved': '#3498db',
            'shipment_rejected': '#e74c3c',
            'user_suspended': '#95a5a6',
            'user_activated': '#2ecc71',
        }
        color = colors.get(obj.action_type, '#34495e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_type_display()
        )
    action_type_badge.short_description = 'İşlem Türü'

    def description_short(self, obj):
        """Show shortened description"""
        return obj.description[:80] + '...' if len(obj.description) > 80 else obj.description
    description_short.short_description = 'Açıklama'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles"""

    list_display = [
        'user_email',
        'phone_number',
        'iban_masked',
        'profile_status',
        'documents_status',
        'created_at',
    ]

    list_filter = [
        'profile_completed',
        'documents_verified',
        'created_at',
    ]

    search_fields = [
        'user__email',
        'user__username',
        'phone_number',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'document_count_display',
        'approved_document_count_display',
    ]

    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'user_type')
        }),
        ('İletişim Bilgileri', {
            'fields': ('phone_number', 'iban')
        }),
        ('Profil Durumu', {
            'fields': ('profile_completed', 'documents_verified', 'document_count_display', 'approved_document_count_display')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'Email'

    def iban_masked(self, obj):
        """Display masked IBAN for privacy"""
        if obj.iban:
            return obj.iban[:4] + '****' + obj.iban[-4:]
        return '-'
    iban_masked.short_description = 'IBAN'

    def profile_status(self, obj):
        """Display profile completion status"""
        if obj.profile_completed:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 10px; border-radius: 3px;">✓ Tamamlandı</span>'
            )
        return format_html(
            '<span style="background-color: #e74c3c; color: white; padding: 3px 10px; border-radius: 3px;">✗ Eksik</span>'
        )
    profile_status.short_description = 'Profil Durumu'

    def documents_status(self, obj):
        """Display document verification status"""
        if obj.documents_verified:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 10px; border-radius: 3px;">✓ Onaylandı</span>'
            )
        return format_html(
            '<span style="background-color: #f39c12; color: white; padding: 3px 10px; border-radius: 3px;">⏳ Bekliyor</span>'
        )
    documents_status.short_description = 'Belgeler'

    def document_count_display(self, obj):
        """Show document count"""
        return f"{obj.get_document_count()} belge"
    document_count_display.short_description = 'Toplam Belge'

    def approved_document_count_display(self, obj):
        """Show approved document count"""
        return f"{obj.get_approved_document_count()} onaylı"
    approved_document_count_display.short_description = 'Onaylı Belge'


class BidInline(admin.StackedInline):
    """Inline admin for bids within shipment detail page"""
    model = Bid
    extra = 0
    can_delete = False

    fields = [
        ('carrier_name', 'carrier_email', 'carrier_verified'),
        ('offered_price', 'estimated_delivery_days', 'status_badge'),
        'message',
        'shipper_comment',
        'created_at',
    ]

    readonly_fields = [
        'carrier_name',
        'carrier_email',
        'carrier_verified',
        'offered_price',
        'estimated_delivery_days',
        'message',
        'created_at',
        'status_badge',
    ]

    def status_badge(self, obj):
        """Display status with colored badge in inline"""
        if not obj.pk:
            return "-"
        colors = {
            'pending': '#f39c12',
            'accepted': '#27ae60',
            'rejected': '#c0392b',
            'withdrawn': '#95a5a6',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold; font-size: 13px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """Comprehensive admin interface for shipments"""

    list_display = [
        'tracking_number',
        'title_short',
        'shipper_info',
        'route_display',
        'cargo_type_badge',
        'price_display',
        'status_badge',
        'bid_count_display',
        'view_count',
        'created_at',
    ]

    list_filter = [
        'status',
        'cargo_type',
        'from_address_city',
        'to_address_city',
        'created_at',
        'pickup_date',
    ]

    search_fields = [
        'tracking_number',
        'title',
        'description',
        'shipper__user__email',
        'shipper__user__username',
        'from_address_city',
        'to_address_city',
    ]

    readonly_fields = [
        'shipment_id',
        'tracking_number',
        'shipper',
        'shipper_email',
        'shipper_phone',
        'created_at',
        'updated_at',
        'view_count',
        'bid_count',
        'bid_summary',
    ]

    fieldsets = (
        ('İlan Bilgileri', {
            'fields': (
                'shipment_id',
                'tracking_number',
                'title',
                'description',
                'cargo_type',
                'status',
            )
        }),
        ('Yük Sahibi', {
            'fields': (
                'shipper',
                'shipper_email',
                'shipper_phone',
            )
        }),
        ('Kalkış Adresi', {
            'fields': (
                'from_address_city',
                'from_address_district',
                'from_address_full',
                ('from_address_lat', 'from_address_lng'),
            )
        }),
        ('Varış Adresi', {
            'fields': (
                'to_address_city',
                'to_address_district',
                'to_address_full',
                ('to_address_lat', 'to_address_lng'),
            )
        }),
        ('Yük Detayları', {
            'fields': (
                'weight',
                ('length', 'width', 'height'),
                ('loading_responsibility', 'unloading_responsibility'),
                'images',
            )
        }),
        ('Fiyat ve Tarihler', {
            'fields': (
                'suggested_price',
                'final_price',
                'pickup_date',
                'delivery_date',
            )
        }),
        ('Atama Bilgileri', {
            'fields': (
                'assigned_bid_id',
                'completed_at',
            ),
            'classes': ('collapse',)
        }),
        ('İstatistikler', {
            'fields': (
                'view_count',
                'bid_count',
                'bid_summary',
                'created_at',
                'updated_at',
            )
        }),
    )

    inlines = [BidInline]

    actions = ['mark_as_active', 'mark_as_assigned', 'mark_as_completed', 'mark_as_cancelled']

    def title_short(self, obj):
        """Show shortened title"""
        return obj.title[:40] + '...' if len(obj.title) > 40 else obj.title
    title_short.short_description = 'İlan Başlığı'

    def shipper_info(self, obj):
        """Display shipper information"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.shipper.user.get_full_name() or obj.shipper.user.username,
            obj.shipper_email
        )
    shipper_info.short_description = 'Yük Sahibi'

    def route_display(self, obj):
        """Display route with arrow"""
        return format_html(
            '<span style="color: #2c3e50;"><strong>{}</strong><br>→ <strong>{}</strong></span>',
            obj.from_address_city,
            obj.to_address_city
        )
    route_display.short_description = 'Rota'

    def cargo_type_badge(self, obj):
        """Display cargo type with colored badge"""
        colors = {
            'evden_eve': '#3498db',
            'isyeri': '#9b59b6',
            'parcali': '#e67e22',
            'arac': '#e74c3c',
            'beyaz_esya': '#1abc9c',
            'mobilya': '#f39c12',
            'arac_ici': '#16a085',
            'diger': '#95a5a6',
        }
        color = colors.get(obj.cargo_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_cargo_type_display()
        )
    cargo_type_badge.short_description = 'Kargo Tipi'

    def price_display(self, obj):
        """Display price information"""
        if obj.final_price:
            return format_html(
                '<strong style="color: #27ae60;">{} ₺</strong><br><small style="text-decoration: line-through;">{} ₺</small>',
                obj.final_price,
                obj.suggested_price
            )
        return format_html('<strong>{} ₺</strong>', obj.suggested_price)
    price_display.short_description = 'Fiyat'

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'active': '#3498db',
            'assigned': '#f39c12',
            'in_transit': '#9b59b6',
            'completed': '#27ae60',
            'cancelled': '#c0392b',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'

    def bid_count_display(self, obj):
        """Display bid count with icon"""
        if obj.bid_count > 0:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">📨 {}</span>',
                obj.bid_count
            )
        return format_html('<span style="color: #95a5a6;">0</span>')
    bid_count_display.short_description = 'Teklifler'

    def bid_summary(self, obj):
        """Show detailed bid summary"""
        bids = obj.bids.all()
        if not bids:
            return "Henüz teklif yok"

        pending = bids.filter(status='pending').count()
        accepted = bids.filter(status='accepted').count()
        rejected = bids.filter(status='rejected').count()

        # Get price range
        prices = [bid.offered_price for bid in bids]
        min_price = min(prices)
        max_price = max(prices)

        return format_html(
            '<strong>Toplam:</strong> {} teklif<br>'
            '<strong>Beklemede:</strong> {} | '
            '<strong>Kabul:</strong> {} | '
            '<strong>Red:</strong> {}<br>'
            '<strong>Fiyat Aralığı:</strong> {} ₺ - {} ₺',
            len(bids),
            pending,
            accepted,
            rejected,
            min_price,
            max_price
        )
    bid_summary.short_description = 'Teklif Özeti'

    def mark_as_active(self, request, queryset):
        """Mark shipments as active"""
        count = queryset.update(status='active')
        self.message_user(request, f"✅ {count} ilan aktif olarak işaretlendi!", 'success')
    mark_as_active.short_description = "📢 Aktif olarak işaretle"

    def mark_as_assigned(self, request, queryset):
        """Mark shipments as assigned"""
        count = queryset.update(status='assigned')
        self.message_user(request, f"✅ {count} ilan atandı olarak işaretlendi!", 'success')
    mark_as_assigned.short_description = "✅ Atandı olarak işaretle"

    def mark_as_completed(self, request, queryset):
        """Mark shipments as completed"""
        count = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"✅ {count} ilan tamamlandı olarak işaretlendi!", 'success')
    mark_as_completed.short_description = "🎉 Tamamlandı olarak işaretle"

    def mark_as_cancelled(self, request, queryset):
        """Mark shipments as cancelled"""
        count = queryset.update(status='cancelled')
        self.message_user(request, f"❌ {count} ilan iptal edildi!", 'warning')
    mark_as_cancelled.short_description = "❌ İptal edildi olarak işaretle"


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    """Admin interface for bids/offers"""

    list_display = [
        'tracking_number',
        'carrier_email',
        'offered_price_display',
        'estimated_delivery_days',
        'status_badge',
        'created_at',
    ]

    list_filter = [
        'status',
        'created_at',
        'estimated_delivery_days',
    ]

    search_fields = [
        'tracking_number',
        'carrier_email',
        'carrier_name',
        'shipper_email',
        'bid_id',
    ]

    readonly_fields = [
        'bid_id',
        'shipment_id',
        'tracking_number',
        'carrier_email',
        'carrier_name',
        'carrier_phone',
        'shipper_email',
        'created_at',
        'updated_at',
    ]

    actions = ['accept_bids', 'reject_bids']

    fieldsets = (
        ('Teklif Bilgileri', {
            'fields': ('bid_id', 'tracking_number', 'shipment_id')
        }),
        ('Taşıyıcı Bilgileri', {
            'fields': ('carrier_email', 'carrier_name', 'carrier_phone', 'carrier_verified')
        }),
        ('Yük Sahibi Bilgileri', {
            'fields': ('shipper_email',)
        }),
        ('Teklif Detayları', {
            'fields': ('offered_price', 'estimated_delivery_days', 'message', 'shipper_comment')
        }),
        ('Durum', {
            'fields': ('status', 'accepted_at')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def offered_price_display(self, obj):
        """Display offered price with currency"""
        return f"{obj.offered_price} ₺"
    offered_price_display.short_description = 'Teklif Fiyatı'

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#f39c12',
            'accepted': '#27ae60',
            'rejected': '#c0392b',
            'withdrawn': '#95a5a6',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'

    def accept_bids(self, request, queryset):
        """Toplu teklif kabul et"""
        count = queryset.filter(status='pending').update(status='accepted')
        self.message_user(request, f"✅ {count} teklif kabul edildi!", 'success')
    accept_bids.short_description = "✅ Seçili teklifleri KABUL ET"

    def reject_bids(self, request, queryset):
        """Toplu teklif reddet"""
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"❌ {count} teklif reddedildi!", 'warning')
    reject_bids.short_description = "❌ Seçili teklifleri REDDET"


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Vehicle Admin - Carrier vehicles management"""
    list_display = [
        'plate_number',
        'carrier_email',
        'brand_model',
        'vehicle_type_display',
        'max_weight_kg',
        'insurance_badge',
        'is_active',
        'created_at',
    ]

    list_filter = [
        'vehicle_type',
        'is_active',
        'has_cargo_insurance',
        'created_at',
    ]

    search_fields = [
        'plate_number',
        'brand',
        'model',
        'carrier_profile__user__email',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Araç Bilgileri', {
            'fields': (
                'carrier_profile',
                'plate_number',
                'brand',
                'model',
                'year',
                'vehicle_type',
            )
        }),
        ('Kapasite', {
            'fields': (
                'max_weight_kg',
                'max_volume_m3',
            )
        }),
        ('Sigorta Bilgileri', {
            'fields': (
                'has_cargo_insurance',
                'insurance_company',
                'insurance_expiry',
            )
        }),
        ('Durum', {
            'fields': (
                'is_active',
                'created_at',
                'updated_at',
            )
        }),
    )

    def carrier_email(self, obj):
        """Display carrier email"""
        return obj.carrier_profile.user.email
    carrier_email.short_description = 'Taşıyıcı'

    def brand_model(self, obj):
        """Display brand and model"""
        return f"{obj.brand} {obj.model} ({obj.year})"
    brand_model.short_description = 'Marka/Model'

    def vehicle_type_display(self, obj):
        """Display vehicle type with icon"""
        icons = {
            0: '🚐',  # Kamyonet
            1: '🚛',  # Kamyon
            2: '🚚',  # TIR
            3: '🚜',  # Çekici
            4: '📦',  # Dorse
        }
        icon = icons.get(obj.vehicle_type, '🚗')
        return format_html(
            '{} {}',
            icon,
            obj.get_vehicle_type_display()
        )
    vehicle_type_display.short_description = 'Araç Tipi'

    def insurance_badge(self, obj):
        """Display insurance status with badge"""
        if obj.has_cargo_insurance:
            if obj.insurance_expiry:
                from django.utils import timezone
                if obj.insurance_expiry < timezone.now().date():
                    return format_html(
                        '<span style="background-color: #e74c3c; color: white; padding: 3px 10px; border-radius: 3px;">⚠️ Süresi Dolmuş</span>'
                    )
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 10px; border-radius: 3px;">✓ Sigortalı</span>'
            )
        return format_html(
            '<span style="background-color: #95a5a6; color: white; padding: 3px 10px; border-radius: 3px;">✗ Sigortasız</span>'
        )
    insurance_badge.short_description = 'Sigorta'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for payment management and transfers"""

    list_display = [
        'payment_id_short',
        'tracking_number_link',
        'shipper_name',
        'carrier_name',
        'amount_display',
        'status_badge',
        'delivery_status',
        'admin_transferred',
        'created_at',
    ]

    list_filter = [
        'status',
        'admin_transferred',
        'created_at',
        'paid_at',
        'shipper_confirmed_delivery',
        'carrier_confirmed_delivery',
    ]

    search_fields = [
        'payment_id',
        'shipment__tracking_number',
        'shipper__user__email',
        'carrier__user__email',
        'transaction_id',
    ]

    readonly_fields = [
        'payment_id',
        'shipment',
        'bid',
        'shipper',
        'carrier',
        'amount',
        'platform_fee',
        'carrier_amount',
        'created_at',
        'paid_at',
        'shipper_confirmed_at',
        'carrier_confirmed_at',
        'admin_transferred_at',
        'completed_at',
        'transaction_details_display',
        'delivery_confirmation_display',
    ]

    fieldsets = (
        ('Ödeme Bilgileri', {
            'fields': (
                'payment_id',
                'shipment',
                'bid',
                'status',
            )
        }),
        ('Taraflar', {
            'fields': (
                'shipper',
                'carrier',
            )
        }),
        ('Tutar Bilgileri', {
            'fields': (
                'amount',
                'platform_fee',
                'carrier_amount',
            )
        }),
        ('Sanal POS Bilgileri', {
            'fields': (
                'payment_method',
                'transaction_id',
                'payment_provider',
                'transaction_details_display',
            )
        }),
        ('Teslim Onayları', {
            'fields': (
                'delivery_confirmation_display',
                'shipper_confirmed_delivery',
                'shipper_confirmed_at',
                'carrier_confirmed_delivery',
                'carrier_confirmed_at',
            )
        }),
        ('Admin Transfer', {
            'fields': (
                'admin_transferred',
                'admin_transferred_by',
                'admin_transferred_at',
                'admin_notes',
            )
        }),
        ('Tarihler', {
            'fields': (
                'created_at',
                'paid_at',
                'completed_at',
            ),
            'classes': ('collapse',)
        }),
    )

    actions = ['transfer_to_carrier']

    def payment_id_short(self, obj):
        """Display short payment ID"""
        return obj.payment_id[:13] + '...'
    payment_id_short.short_description = 'Ödeme ID'

    def tracking_number_link(self, obj):
        """Display tracking number with link to shipment"""
        url = reverse('admin:website_shipment_change', args=[obj.shipment.shipment_id])
        return format_html(
            '<a href="{}" style="color: #3498db; font-weight: bold;">{}</a>',
            url,
            obj.shipment.tracking_number
        )
    tracking_number_link.short_description = 'Takip No'

    def shipper_name(self, obj):
        """Display shipper name and email"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.shipper.user.get_full_name() or obj.shipper.user.username,
            obj.shipper.user.email
        )
    shipper_name.short_description = 'Yük Sahibi'

    def carrier_name(self, obj):
        """Display carrier name and email"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.carrier.user.get_full_name() or obj.carrier.user.username,
            obj.carrier.user.email
        )
    carrier_name.short_description = 'Taşıyıcı'

    def amount_display(self, obj):
        """Display amount breakdown"""
        return format_html(
            '<strong style="color: #27ae60;">{} ₺</strong><br>'
            '<small>Komisyon: {} ₺</small><br>'
            '<small>Taşıyıcı: {} ₺</small>',
            obj.amount,
            obj.platform_fee,
            obj.carrier_amount
        )
    amount_display.short_description = 'Tutar'

    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#f39c12',
            'paid': '#3498db',
            'in_transit': '#9b59b6',
            'delivered': '#16a085',
            'completed': '#27ae60',
            'refunded': '#e74c3c',
            'disputed': '#c0392b',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'

    def delivery_status(self, obj):
        """Display delivery confirmation status"""
        shipper_icon = '✅' if obj.shipper_confirmed_delivery else '⏳'
        carrier_icon = '✅' if obj.carrier_confirmed_delivery else '⏳'

        if obj.is_delivery_confirmed():
            color = '#27ae60'
            text = 'Her İki Taraf Onayladı'
        else:
            color = '#f39c12'
            text = 'Onay Bekleniyor'

        return format_html(
            '<span style="color: {};">{} Yük Sahibi | {} Taşıyıcı</span><br>'
            '<small>{}</small>',
            color,
            shipper_icon,
            carrier_icon,
            text
        )
    delivery_status.short_description = 'Teslim Durumu'

    def transaction_details_display(self, obj):
        """Display transaction details in readonly field"""
        if obj.transaction_id:
            return format_html(
                '<strong>İşlem ID:</strong> {}<br>'
                '<strong>Sağlayıcı:</strong> {}<br>'
                '<strong>Yöntem:</strong> {}',
                obj.transaction_id,
                obj.payment_provider or 'Belirtilmemiş',
                obj.payment_method
            )
        return 'Henüz ödeme yapılmamış'
    transaction_details_display.short_description = 'İşlem Detayları'

    def delivery_confirmation_display(self, obj):
        """Display delivery confirmation summary"""
        return format_html(
            '<table style="border-collapse: collapse; width: 100%;">'
            '<tr><td style="padding: 5px;"><strong>Yük Sahibi:</strong></td><td style="padding: 5px;">{}</td><td style="padding: 5px;">{}</td></tr>'
            '<tr><td style="padding: 5px;"><strong>Taşıyıcı:</strong></td><td style="padding: 5px;">{}</td><td style="padding: 5px;">{}</td></tr>'
            '</table>',
            '✅ Onaylandı' if obj.shipper_confirmed_delivery else '⏳ Bekliyor',
            obj.shipper_confirmed_at.strftime('%d.%m.%Y %H:%M') if obj.shipper_confirmed_at else '-',
            '✅ Onaylandı' if obj.carrier_confirmed_delivery else '⏳ Bekliyor',
            obj.carrier_confirmed_at.strftime('%d.%m.%Y %H:%M') if obj.carrier_confirmed_at else '-',
        )
    delivery_confirmation_display.short_description = 'Teslim Onay Özeti'

    def transfer_to_carrier(self, request, queryset):
        """Admin action to transfer money to carrier"""
        count = 0
        errors = []

        for payment in queryset:
            if payment.can_transfer_to_carrier():
                payment.status = 'completed'
                payment.admin_transferred = True
                payment.admin_transferred_by = request.user
                payment.admin_transferred_at = timezone.now()
                payment.completed_at = timezone.now()
                payment.save()
                count += 1

                # Log activity
                AdminActivity.objects.create(
                    admin_user=request.user,
                    action_type='document_approved',  # TODO: Add payment_transferred type
                    target_type='payment',
                    target_id=payment.payment_id,
                    description=f"Ödeme taşıyıcıya transfer edildi - {payment.carrier_amount} ₺ - {payment.carrier.user.email}",
                    ip_address=self.get_client_ip(request)
                )
            else:
                reason = []
                if payment.status != 'delivered':
                    reason.append(f"Durum 'Teslim Edildi' değil ({payment.get_status_display()})")
                if not payment.is_delivery_confirmed():
                    reason.append("Her iki taraf teslim onayı vermemiş")
                if payment.admin_transferred:
                    reason.append("Zaten transfer edilmiş")

                errors.append(f"{payment.payment_id[:8]}: {', '.join(reason)}")

        if count > 0:
            self.message_user(
                request,
                f"✅ {count} ödeme taşıyıcıya başarıyla transfer edildi! ({count * list(queryset)[0].carrier_amount if count == 1 else 'toplam'} ₺)",
                'success'
            )

        if errors:
            error_msg = "Bazı ödemeler transfer edilemedi:<br>" + "<br>".join(errors)
            self.message_user(request, format_html(error_msg), 'warning')

        if count == 0 and not errors:
            self.message_user(request, "Hiçbir ödeme transfer edilemedi. Lütfen ödeme durumunu kontrol edin.", 'error')

    transfer_to_carrier.short_description = "💰 Seçili ödemeleri taşıyıcıya transfer et"

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Custom admin index view with dashboard
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from .admin_dashboard import AdminDashboard


class NakliyeNetAdminSite(AdminSite):
    """Custom admin site with dashboard"""
    site_header = "NAKLIYE NET Yönetim Paneli"
    site_title = "NAKLIYE NET Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        """Custom admin index with statistics dashboard"""
        # Get dashboard statistics
        stats = AdminDashboard.get_dashboard_stats()
        dashboard_html = AdminDashboard.render_dashboard_html(stats)

        extra_context = extra_context or {}
        extra_context['dashboard_html'] = dashboard_html

        return super().index(request, extra_context)


# Replace default admin site
admin_site = NakliyeNetAdminSite(name='admin')

# Re-register all models with the new admin site
admin_site.register(UserDocument, UserDocumentAdmin)
admin_site.register(AdminActivity, AdminActivityAdmin)
admin_site.register(UserProfile, UserProfileAdmin)
admin_site.register(Shipment, ShipmentAdmin)
admin_site.register(Bid, BidAdmin)
admin_site.register(Vehicle, VehicleAdmin)
admin_site.register(Payment, PaymentAdmin)

# Register django.contrib.sites and allauth models for OAuth configuration
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken

admin_site.register(Site)
admin_site.register(SocialApp)
admin_site.register(SocialAccount)
admin_site.register(SocialToken)
