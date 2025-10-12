# Firebase Authentication System - NAKLIYE NET

Complete authentication system integrated with Firebase Auth for the Django web application.

## Overview

This authentication system provides:
- Email/Password login and registration
- Google Sign-In (OAuth)
- User profile management
- Password reset functionality
- Firebase Firestore user data synchronization
- Compatibility with mobile apps (same Firebase Auth backend)

## Features Implemented

### 1. Authentication Views

- **Login** (`/giris/`) - Email/password & Google sign-in
- **Register** (`/kayit/`) - New user registration with user type selection
- **Logout** (`/cikis/`) - Sign out functionality
- **Profile** (`/profil/`) - User profile management
- **Password Reset** (`/sifre-sifirlama/`) - Firebase password reset

### 2. Firebase Integration

- **Backend**: Firebase Admin SDK for server-side operations
- **Frontend**: Firebase Client SDK for authentication
- **Firestore**: User profiles stored in `users` collection
- **Sync**: Same user data structure as mobile apps

### 3. User Data Structure (Firestore)

```javascript
{
  uid: "firebase-user-id",
  email: "user@example.com",
  displayName: "Ad Soyad",
  phoneNumber: "+90 555 123 4567",
  photoURL: "https://...",
  userType: 0,  // 0: Shipper, 1: Carrier
  isActive: true,
  isEmailVerified: false,
  isPhoneVerified: false,
  completedShipments: 0,
  rating: 0.0,
  reviewCount: 0,
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

## Setup Instructions

### 1. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:

```env
# Firebase Admin SDK (Backend)
FIREBASE_CREDENTIALS_PATH=firebase-adminsdk.json
# OR for production:
# FIREBASE_CREDENTIALS_BASE64=base64-encoded-credentials

# Firebase Client SDK (Frontend)
FIREBASE_API_KEY=AIzaSy...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789012
FIREBASE_APP_ID=1:123456:web:abc123

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

### 2. Firebase Console Setup

#### A. Get Firebase Client SDK Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** > **General**
4. Scroll to **Your apps** section
5. Click **Web app** (</> icon) if not created yet
6. Copy the configuration values to `.env`

#### B. Enable Authentication Methods

1. Go to **Authentication** > **Sign-in method**
2. Enable:
   - **Email/Password**
   - **Google** (configure OAuth)

#### C. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project
3. Go to **APIs & Services** > **Credentials**
4. Create OAuth 2.0 Client ID (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `https://nakliyenet.com/accounts/google/login/callback/`
6. Copy Client ID and Client Secret to `.env`

#### D. Firebase Admin SDK

Already configured in your project as `firebase-adminsdk.json`

### 3. Django Configuration

Already configured in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'website.firebase_auth.FirebaseAuthenticationBackend',
]
```

### 4. Database Migration

Run migrations to create authentication tables:

```bash
python manage.py migrate
```

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

## Usage

### For Users

1. **Register**: Go to `/kayit/`
   - Choose user type (Yük Sahibi / Taşıyıcı)
   - Fill in email, name, password
   - Or use Google Sign-In

2. **Login**: Go to `/giris/`
   - Use email/password
   - Or use Google Sign-In

3. **Profile**: Go to `/profil/` (after login)
   - View stats (completed shipments, rating, reviews)
   - Edit profile information
   - Change password
   - Verify email

4. **Password Reset**: Go to `/sifre-sifirlama/`
   - Enter email
   - Check email for reset link

### For Developers

#### Custom Authentication Backend

Located in `website/firebase_auth.py`:

```python
from website.firebase_auth import firebase_auth_service

# Create user
user = firebase_auth_service.create_user(
    email='user@example.com',
    password='password123',
    display_name='User Name'
)

# Get user
user = firebase_auth_service.get_user_by_email('user@example.com')

# Update user
firebase_auth_service.update_user(
    uid='firebase-uid',
    display_name='New Name'
)

# Get Firestore profile
profile = firebase_auth_service.get_firestore_profile('firebase-uid')
```

#### Protecting Views

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    # Get Firebase UID
    firebase_uid = request.user.username

    # Get Firestore profile
    profile = firebase_auth_service.get_firestore_profile(firebase_uid)

    return render(request, 'template.html', {'profile': profile})
```

## File Structure

```
nakliyenet_django/
├── website/
│   ├── firebase_auth.py          # Firebase authentication backend
│   ├── auth_views.py              # Authentication views
│   └── urls.py                    # URL configuration (includes auth URLs)
├── templates/
│   ├── base.html                  # Updated with auth navigation
│   └── website/
│       ├── login.html             # Login page
│       ├── register.html          # Registration page
│       ├── profile.html           # User profile
│       ├── password_reset.html    # Password reset request
│       ├── password_reset_done.html
│       └── password_reset_confirm.html
├── nakliyenet/
│   ├── settings.py                # Updated with auth config
│   └── urls.py                    # Includes allauth URLs
└── .env.example                   # Environment variables template
```

## Security Considerations

### Implemented Security Features

1. **CSRF Protection**: Enabled on all forms
2. **Password Validation**: Django's built-in validators
3. **Secure Sessions**: HTTPOnly cookies
4. **Firebase Token Verification**: Server-side verification
5. **HTTPS Redirect**: In production (configured in settings.py)

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use HTTPS for all traffic
- [ ] Set secure session cookies:
  ```python
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  ```
- [ ] Use Firebase credentials via base64 environment variable
- [ ] Configure proper CORS settings
- [ ] Enable Firebase App Check (mobile apps)
- [ ] Set up email verification
- [ ] Configure rate limiting

## API Endpoints

### Check Email Availability

```javascript
POST /api/check-email/
{
  "email": "user@example.com"
}

Response:
{
  "exists": true
}
```

### Verify Firebase Token

```javascript
POST /api/verify-token/
{
  "token": "firebase-id-token"
}

Response:
{
  "valid": true,
  "uid": "firebase-user-id",
  "email": "user@example.com"
}
```

## Troubleshooting

### Common Issues

#### 1. Firebase Credentials Not Found

**Error**: `FileNotFoundError: Firebase credentials not found`

**Solution**:
- Check `firebase-adminsdk.json` exists in project root
- Or set `FIREBASE_CREDENTIALS_BASE64` environment variable

#### 2. Google Sign-In Not Working

**Error**: Google popup closes without signing in

**Solution**:
- Check `FIREBASE_API_KEY` in `.env`
- Verify authorized domains in Firebase Console
- Check OAuth redirect URIs in Google Cloud Console

#### 3. Email Already Exists

**Error**: `firebase_auth.EmailAlreadyExistsError`

**Solution**:
- User already registered
- Use password reset to recover account
- Or sign in with existing credentials

#### 4. Token Verification Failed

**Error**: `Invalid Firebase ID token`

**Solution**:
- Check Firebase configuration in templates
- Verify API key is correct
- Check browser console for JavaScript errors

### Debug Mode

Enable debug logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'website.firebase_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Testing

### Manual Testing Checklist

- [ ] Register new user with email/password
- [ ] Register new user with Google Sign-In
- [ ] Login with email/password
- [ ] Login with Google Sign-In
- [ ] View profile page
- [ ] Edit profile information
- [ ] Request password reset
- [ ] Logout
- [ ] Verify email works
- [ ] Check Firestore user document created

### Test Accounts

Create test accounts in Firebase Console for testing:
- **Email**: test@nakliyenet.com
- **Password**: Test123456

## Mobile App Integration

This authentication system is compatible with the mobile apps because:

1. **Same Firebase Project**: Uses same Firebase Auth backend
2. **Same User Structure**: Firestore users collection structure matches
3. **Cross-Platform**: Users can login on web and mobile with same credentials
4. **Real-time Sync**: User profile changes sync across all platforms

## Support

For issues or questions:
- Check Firebase Console logs
- Review Django logs: `python manage.py runserver`
- Check browser console for JavaScript errors
- Contact: support@nakliyenet.com

## Next Steps

1. **Email Verification**:
   - Configure email templates in Firebase Console
   - Enable email verification on registration

2. **Phone Verification**:
   - Add phone verification flow
   - Update Firestore on verification

3. **Two-Factor Authentication**:
   - Add 2FA using Firebase Phone Auth
   - Integrate with profile settings

4. **Social Login**:
   - Add Facebook login
   - Add Apple Sign-In

5. **Advanced Features**:
   - Add user roles and permissions
   - Implement account deletion flow
   - Add account linking (merge accounts)

## License

This authentication system is part of the NAKLIYE NET project.

---

**Last Updated**: 2025-10-08
**Version**: 1.0.0
