"""
Custom Google OAuth Views - Simple and reliable
"""
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import UserProfile
from django.conf import settings
import requests
import logging
import secrets

logger = logging.getLogger(__name__)


def google_login_start(request):
    """
    Start Google OAuth login - Redirect to Google
    """
    # Google OAuth configuration
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID if hasattr(settings, 'GOOGLE_OAUTH_CLIENT_ID') else None

    if not client_id:
        # Try to get from database
        from allauth.socialaccount.models import SocialApp
        try:
            google_app = SocialApp.objects.get(provider='google')
            client_id = google_app.client_id
        except:
            return HttpResponse("Google OAuth not configured", status=500)

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state

    # Build Google OAuth URL
    redirect_uri = request.build_absolute_uri('/oauth/google/callback/')

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"redirect_uri={redirect_uri}&"
        f"state={state}"
    )

    return redirect(google_auth_url)


@csrf_exempt
def google_oauth_callback(request):
    """
    Handle Google OAuth callback
    """
    # Get authorization code from Google
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    if error:
        logger.error(f"Google OAuth error: {error}")
        return HttpResponse(f"Google OAuth Error: {error}", status=400)

    if not code:
        return HttpResponse("No authorization code received", status=400)

    # Verify state (CSRF protection)
    saved_state = request.session.get('oauth_state')
    if state != saved_state:
        logger.error(f"OAuth state mismatch: {state} != {saved_state}")
        # Don't fail for now, just log

    # Get Google credentials
    from allauth.socialaccount.models import SocialApp
    try:
        google_app = SocialApp.objects.get(provider='google')
        client_id = google_app.client_id
        client_secret = google_app.secret
    except Exception as e:
        logger.error(f"Failed to get Google app: {e}")
        return HttpResponse(f"Configuration error: {e}", status=500)

    # Exchange code for access token
    redirect_uri = request.build_absolute_uri('/oauth/google/callback/')
    token_url = "https://oauth2.googleapis.com/token"

    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
    except Exception as e:
        logger.error(f"Failed to exchange code for token: {e}")
        return HttpResponse(f"Token exchange failed: {e}", status=500)

    access_token = tokens.get('access_token')
    if not access_token:
        return HttpResponse("No access token received", status=500)

    # Get user info from Google
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        return HttpResponse(f"Failed to get user info: {e}", status=500)

    # Extract user data
    email = user_info.get('email')
    given_name = user_info.get('given_name', '')
    family_name = user_info.get('family_name', '')
    google_id = user_info.get('id')

    if not email:
        return HttpResponse("No email in Google response", status=400)

    # Get or create user
    try:
        user = User.objects.get(email=email)
        logger.info(f"Existing user found: {email}")
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=given_name,
            last_name=family_name
        )
        user.set_unusable_password()  # No password for OAuth users
        user.save()
        logger.info(f"New user created: {email}")

        # Create UserProfile
        try:
            UserProfile.objects.create(
                user=user,
                user_type=0,  # Default: shipper (Yük Veren)
            )
            logger.info(f"UserProfile created for: {email}")
        except Exception as e:
            logger.error(f"Failed to create UserProfile: {e}")

    # Log the user in
    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    logger.info(f"User logged in: {email}")

    # Redirect to profile or home
    return redirect('/profilim/')


def google_login_debug(request):
    """
    Google OAuth callback - Debug version
    """
    # Log everything
    logger.error(f"=== GOOGLE OAUTH CALLBACK DEBUG ===")
    logger.error(f"GET params: {dict(request.GET)}")
    logger.error(f"POST params: {dict(request.POST)}")

    html = f"""<!DOCTYPE html>
<html><head><title>OAuth Debug</title>
<style>
body {{ font-family: monospace; padding: 20px; }}
pre {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
h2 {{ color: #0d6efd; }}
</style></head>
<body>
<h1>Google OAuth Callback Debug</h1>
<h2>GET:</h2><pre>{request.GET}</pre>
<h2>POST:</h2><pre>{request.POST}</pre>
<h2>URL:</h2><pre>{request.build_absolute_uri()}</pre>
<p><a href="/">Ana Sayfa</a></p>
</body></html>"""

    return HttpResponse(html)
