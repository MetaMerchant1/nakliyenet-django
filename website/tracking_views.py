"""
Tracking Views - Shipment tracking and delivery confirmation
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Shipment, Bid, ShipmentTracking, DeliveryProof, Review


def shipment_tracking(request, tracking_number):
    """
    Shipment tracking page - Shows tracking timeline
    Public view - anyone can see tracking info
    """
    # Get shipment
    try:
        shipment = Shipment.objects.select_related('shipper__user').get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        raise Http404("İlan bulunamadı")

    # Get tracking updates
    tracking_updates = ShipmentTracking.objects.filter(
        shipment=shipment
    ).select_related('updated_by__user').order_by('-created_at')

    # Get delivery proofs
    delivery_proofs = DeliveryProof.objects.filter(
        shipment=shipment
    ).select_related('uploaded_by__user').order_by('-created_at')

    # Get assigned bid/carrier
    assigned_bid = None
    if shipment.assigned_bid_id:
        try:
            assigned_bid = Bid.objects.select_related('carrier__user').get(bid_id=shipment.assigned_bid_id)
        except Bid.DoesNotExist:
            pass

    context = {
        'title': f'{shipment.tracking_number} - Gönderi Takibi',
        'description': f'{shipment.title} gönderi takip bilgileri',
        'shipment': shipment,
        'tracking_updates': tracking_updates,
        'delivery_proofs': delivery_proofs,
        'assigned_bid': assigned_bid,
    }
    return render(request, 'website/shipment_tracking.html', context)


@login_required
def update_tracking(request, tracking_number):
    """
    Update shipment tracking status - Only carrier can update
    """
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        messages.error(request, 'İlan bulunamadı.')
        return redirect('website:ilanlar')

    # Check if user is the assigned carrier
    profile = request.user.profile
    assigned_bid = Bid.objects.filter(shipment=shipment, status='accepted').first()

    if not assigned_bid or assigned_bid.carrier != profile:
        messages.error(request, 'Bu işlemi yapma yetkiniz yok.')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        location = request.POST.get('location', '').strip()
        note = request.POST.get('note', '').strip()

        # Check payment status before allowing delivery
        if new_status == 'delivered':
            from .models import Payment
            try:
                payment = Payment.objects.get(shipment=shipment)
                if payment.status not in ['paid', 'in_transit', 'delivered']:
                    messages.error(request, 'Yükü teslim edebilmek için önce ödeme yapılması gerekiyor. Yük sahibi henüz ödeme yapmadı.')
                    return redirect('website:shipment_tracking', tracking_number=tracking_number)
            except Payment.DoesNotExist:
                messages.error(request, 'Ödeme kaydı bulunamadı. Yük sahibi henüz ödeme yapmadı.')
                return redirect('website:shipment_tracking', tracking_number=tracking_number)

        # Status display map
        status_displays = {
            'assigned': 'Taşıyıcı atandı',
            'picked_up': f'Yük {shipment.from_address_city} lokasyonundan toplandı',
            'in_transit': 'Yük yolda',
            'delivered': f'Yük {shipment.to_address_city} adresine teslim edildi',
        }

        # Update shipment status
        shipment.status = new_status
        shipment.save()

        # Create tracking update
        ShipmentTracking.objects.create(
            shipment=shipment,
            status=new_status,
            status_display=status_displays.get(new_status, new_status),
            location=location,
            note=note,
            updated_by=profile,
            is_automatic=False
        )

        messages.success(request, 'Durum başarıyla güncellendi!')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    # GET - show form
    context = {
        'title': f'Durum Güncelle - {tracking_number}',
        'shipment': shipment,
        'current_status': shipment.status,
        'status_choices': Shipment.STATUS_CHOICES,
    }
    return render(request, 'website/update_tracking.html', context)


@login_required
def confirm_delivery(request, tracking_number):
    """
    Confirm delivery and upload delivery proof - Shipper confirms delivery
    """
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        messages.error(request, 'İlan bulunamadı.')
        return redirect('website:ilanlar')

    # Check if user is the shipper
    profile = request.user.profile
    if shipment.shipper != profile:
        messages.error(request, 'Bu işlemi yapma yetkiniz yok.')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    # Check if shipment is delivered
    if shipment.status != 'delivered':
        messages.error(request, 'Gönderi henüz teslim edilmedi.')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    if request.method == 'POST':
        # Mark as completed
        shipment.status = 'completed'
        shipment.completed_at = timezone.now()
        shipment.save()

        # Create tracking update
        ShipmentTracking.objects.create(
            shipment=shipment,
            status='completed',
            status_display='Teslimat onaylandı - İşlem tamamlandı',
            note='Yük sahibi teslimatı onayladı',
            updated_by=profile,
            is_automatic=False
        )

        messages.success(request, 'Teslimat onaylandı! Artık taşıyıcıyı değerlendirebilirsiniz.')
        return redirect('website:add_review', tracking_number=tracking_number)

    context = {
        'title': f'Teslimatı Onayla - {tracking_number}',
        'shipment': shipment,
    }
    return render(request, 'website/confirm_delivery.html', context)


@login_required
def add_review(request, tracking_number):
    """
    Add review for completed shipment
    Both shipper and carrier can review each other
    """
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        messages.error(request, 'İlan bulunamadı.')
        return redirect('website:ilanlar')

    # Get assigned bid
    assigned_bid = Bid.objects.filter(shipment=shipment, status='accepted').first()
    if not assigned_bid:
        messages.error(request, 'Bu gönderiye atanmış taşıyıcı bulunamadı.')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    # Check authorization
    profile = request.user.profile
    is_shipper = (profile == shipment.shipper)
    is_carrier = (profile == assigned_bid.carrier)

    if not (is_shipper or is_carrier):
        messages.error(request, 'Bu işlemi yapma yetkiniz yok.')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    # Check if already reviewed
    existing_review = Review.objects.filter(shipment=shipment, reviewer=profile).first()
    if existing_review:
        messages.warning(request, 'Bu gönderi için zaten değerlendirme yaptınız.')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        communication_rating = int(request.POST.get('communication_rating', 5))
        professionalism_rating = int(request.POST.get('professionalism_rating', 5))
        punctuality_rating = int(request.POST.get('punctuality_rating', 5))
        comment = request.POST.get('comment', '').strip()

        # Determine who is being reviewed
        if is_shipper:
            reviewed = assigned_bid.carrier
        else:
            reviewed = shipment.shipper

        # Create review
        Review.objects.create(
            shipment=shipment,
            bid=assigned_bid,
            reviewer=profile,
            reviewed=reviewed,
            rating=rating,
            communication_rating=communication_rating,
            professionalism_rating=professionalism_rating,
            punctuality_rating=punctuality_rating,
            comment=comment,
            is_shipper_review=is_shipper
        )

        messages.success(request, 'Değerlendirmeniz kaydedildi. Teşekkürler!')
        return redirect('website:shipment_tracking', tracking_number=tracking_number)

    # Determine who will be reviewed
    if is_shipper:
        reviewed_user = assigned_bid.carrier
        reviewed_role = 'Taşıyıcı'
    else:
        reviewed_user = shipment.shipper
        reviewed_role = 'Yük Sahibi'

    context = {
        'title': f'Değerlendirme Yap - {tracking_number}',
        'shipment': shipment,
        'reviewed_user': reviewed_user,
        'reviewed_role': reviewed_role,
        'is_shipper': is_shipper,
    }
    return render(request, 'website/add_review.html', context)
