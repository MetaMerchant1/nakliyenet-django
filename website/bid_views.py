"""
Bid Management Views - Teklif İşlemleri
Handles bid actions: accept, reject, counter-offer, comments
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
import json
import uuid
from .models import Bid, BidComment, Shipment, UserProfile


@login_required
@require_POST
def bid_accept(request, bid_id):
    """
    Accept a bid - Only shipment owner can accept
    """
    try:
        bid = get_object_or_404(Bid, bid_id=bid_id)

        # Check if user is the shipment owner
        if request.user.profile != bid.shipment.shipper:
            return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yok'}, status=403)

        # Check if bid is still pending
        if bid.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Bu teklif artık beklemede değil'}, status=400)

        # Accept the bid
        bid.status = 'accepted'
        bid.accepted_at = timezone.now()
        bid.save()

        # Update shipment status
        shipment = bid.shipment
        shipment.status = 'assigned'
        shipment.assigned_bid_id = bid_id
        shipment.final_price = bid.get_final_price()
        shipment.save()

        # Reject all other pending bids
        Bid.objects.filter(
            shipment=shipment,
            status='pending'
        ).exclude(bid_id=bid_id).update(
            status='rejected',
            rejected_at=timezone.now()
        )

        return JsonResponse({'success': True, 'message': 'Teklif kabul edildi'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def bid_reject(request, bid_id):
    """
    Reject a bid - Only shipment owner can reject
    """
    try:
        bid = get_object_or_404(Bid, bid_id=bid_id)

        # Check if user is the shipment owner
        if request.user.profile != bid.shipment.shipper:
            return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yok'}, status=403)

        # Check if bid is still pending
        if bid.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Bu teklif artık beklemede değil'}, status=400)

        # Reject the bid
        bid.status = 'rejected'
        bid.rejected_at = timezone.now()
        bid.save()

        return JsonResponse({'success': True, 'message': 'Teklif reddedildi'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def bid_counter_offer(request, bid_id):
    """
    Make a counter offer - Only shipment owner can counter-offer
    """
    try:
        bid = get_object_or_404(Bid, bid_id=bid_id)

        # Check if user is the shipment owner
        if request.user.profile != bid.shipment.shipper:
            return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yok'}, status=403)

        # Check if bid is still pending
        if bid.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Bu teklif artık beklemede değil'}, status=400)

        # Parse request body
        data = json.loads(request.body)
        counter_offer_price = data.get('counter_offer_price')
        counter_offer_message = data.get('counter_offer_message', '')

        if not counter_offer_price:
            return JsonResponse({'success': False, 'error': 'Karşı teklif fiyatı gerekli'}, status=400)

        # Update bid with counter offer
        bid.counter_offer_price = counter_offer_price
        bid.counter_offer_message = counter_offer_message
        bid.counter_offered_at = timezone.now()
        bid.status = 'counter_offered'
        bid.save()

        return JsonResponse({'success': True, 'message': 'Karşı teklif gönderildi'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def bid_comment(request, bid_id):
    """
    Add a comment to a bid - Both shipper and carrier can comment
    """
    try:
        bid = get_object_or_404(Bid, bid_id=bid_id)

        # Check if user is either shipper or carrier
        user_profile = request.user.profile
        is_shipper = (user_profile == bid.shipment.shipper)
        is_carrier = (user_profile == bid.carrier)

        if not (is_shipper or is_carrier):
            messages.error(request, 'Bu teklif üzerine yorum yapma yetkiniz yok')
            return redirect('website:ilan_detay', tracking_number=bid.tracking_number)

        # Get comment from POST
        comment_text = request.POST.get('comment', '').strip()

        if not comment_text:
            messages.error(request, 'Yorum boş olamaz')
            return redirect('website:ilan_detay', tracking_number=bid.tracking_number)

        # Create comment
        BidComment.objects.create(
            bid=bid,
            author=user_profile,
            author_email=request.user.email,
            author_name=request.user.get_full_name() or request.user.username,
            is_shipper=is_shipper,
            comment=comment_text
        )

        messages.success(request, 'Yorumunuz eklendi')
        return redirect('website:ilan_detay', tracking_number=bid.tracking_number)

    except Exception as e:
        messages.error(request, f'Hata: {str(e)}')
        return redirect('website:ilanlar')
