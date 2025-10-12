"""
Authentication Views - Django auth + django-allauth for Google OAuth
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import UserProfile
import logging
import json

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Login page - Email/Password authentication
    Google OAuth handled by django-allauth
    """
    if request.user.is_authenticated:
        return redirect('website:index')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')

        if email and password:
            # Django username/password authentication
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Giriş başarılı! Hoş geldiniz.')
                return redirect(request.GET.get('next', 'website:index'))
            else:
                messages.error(request, 'E-posta veya şifre hatalı.')
        else:
            messages.error(request, 'Lütfen e-posta ve şifrenizi girin.')

    context = {
        'title': 'Giriş Yap - NAKLIYE NET',
        'description': 'NAKLIYE NET platformuna giriş yapın.',
    }
    return render(request, 'website/login.html', context)


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Register page - Create new Django user
    """
    if request.user.is_authenticated:
        return redirect('website:index')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        display_name = request.POST.get('display_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        user_type = request.POST.get('user_type', '0')  # 0: Shipper, 1: Carrier

        # Validation
        if not email or not password:
            messages.error(request, 'E-posta ve şifre zorunludur.')
        elif password != password2:
            messages.error(request, 'Şifreler eşleşmiyor.')
        elif len(password) < 6:
            messages.error(request, 'Şifre en az 6 karakter olmalıdır.')
        elif User.objects.filter(username=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
        else:
            try:
                # Create Django user
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )

                # Split display_name into first_name and last_name
                if display_name:
                    name_parts = display_name.split(' ', 1)
                    user.first_name = name_parts[0]
                    if len(name_parts) > 1:
                        user.last_name = name_parts[1]
                    user.save()

                # UserProfile will be created by signal
                # Update it with additional info
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.user_type = int(user_type)
                profile.phone_number = phone_number
                profile.save()

                # Auto login after registration
                login(request, user)

                messages.success(request, 'Kayıt başarılı! Hoş geldiniz.')
                return redirect('website:index')

            except Exception as e:
                logger.error(f"Registration error: {e}", exc_info=True)
                messages.error(request, 'Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.')

    context = {
        'title': 'Kayıt Ol - NAKLIYE NET',
        'description': 'NAKLIYE NET platformuna üye olun.',
    }
    return render(request, 'website/register.html', context)


@login_required
def profil_view(request):
    """
    User profile view (redirects to profil function in views.py)
    """
    return redirect('website:profil')


@login_required
def logout_view(request):
    """
    Logout user
    """
    logout(request)
    messages.success(request, 'Çıkış yapıldı.')
    return redirect('website:index')


@require_http_methods(["POST"])
def api_check_email(request):
    """
    API endpoint to check if email exists
    """
    try:
        data = json.loads(request.body) if request.body else {}
        email = data.get('email', '').strip()

        if not email:
            return JsonResponse({'error': 'Email required'}, status=400)

        exists = User.objects.filter(username=email).exists()

        return JsonResponse({
            'exists': exists,
            'email': email
        })

    except Exception as e:
        logger.error(f"Check email error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
