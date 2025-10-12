# Quick Start Guide - Firebase Authentication

Get the authentication system up and running in 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Firebase project created
- `firebase-adminsdk.json` file in project root

## Step 1: Install Dependencies (Already Done)

```bash
pip install -r requirements.txt
```

Dependencies installed:
- Django 4.2.8
- django-allauth 0.57.0
- firebase-admin 6.3.0
- And all required packages

## Step 2: Configure Environment Variables

### Option A: For Local Testing (Quick Start)

Create a `.env` file:

```bash
cp .env.example .env
```

Add minimal configuration (just for testing):

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=firebase-adminsdk.json

# Firebase Client SDK (Get from Firebase Console)
FIREBASE_API_KEY=AIzaSy...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
```

**Where to find Firebase Client SDK credentials:**
1. Go to https://console.firebase.google.com/
2. Select your project
3. Click gear icon → Project Settings
4. Scroll down to "Your apps" section
5. Click "Web app" icon (</>)
6. Copy the config values

### Option B: Use Existing Environment (Recommended)

Your existing `.env` should already have most settings. Just add:

```env
FIREBASE_API_KEY=your-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
```

## Step 3: Enable Firebase Authentication

1. Go to Firebase Console
2. Click **Authentication** in left menu
3. Click **Sign-in method** tab
4. Enable **Email/Password**:
   - Click on "Email/Password"
   - Toggle "Enable"
   - Click "Save"

## Step 4: Run Database Migrations (Already Done)

```bash
python manage.py migrate
```

This creates the necessary database tables for authentication.

## Step 5: Start the Development Server

```bash
python manage.py runserver
```

## Step 6: Test Authentication

### Test Registration

1. Open browser: http://localhost:8000/kayit/
2. Fill in the form:
   - Select user type (Yük Sahibi or Taşıyıcı)
   - Enter name, email, password
3. Click "Kayıt Ol"
4. You should be redirected to login page

### Test Login

1. Go to: http://localhost:8000/giris/
2. Enter your email and password
3. Click "Giriş Yap"
4. You should see the home page with your name in navbar

### Test Profile

1. Click on your name in navbar
2. Select "Profilim" from dropdown
3. You should see your profile page with stats
4. Try editing your profile

### Verify in Firestore

1. Go to Firebase Console
2. Click "Firestore Database"
3. Look for "users" collection
4. You should see your user document

## Troubleshooting

### Issue: "Firebase credentials not found"

**Solution**:
- Make sure `firebase-adminsdk.json` exists in project root
- Check `FIREBASE_CREDENTIALS_PATH` in `.env`

### Issue: "Firebase API Key not configured"

**Solution**:
- Add `FIREBASE_API_KEY` and related vars to `.env`
- Check Firebase Console for correct values

### Issue: "Cannot authenticate"

**Solution**:
- Enable Email/Password in Firebase Console
- Check browser console for JavaScript errors
- Verify Firebase config in `.env`

### Issue: "Google Sign-In not working"

**Solution**:
- Google OAuth requires additional setup (see AUTHENTICATION_SETUP.md)
- For now, use email/password authentication

## What's Next?

Now that basic authentication is working:

1. **Configure Google OAuth** (optional):
   - Follow instructions in `AUTHENTICATION_SETUP.md`
   - Set up OAuth credentials in Google Cloud Console

2. **Customize Email Templates**:
   - Configure password reset emails in Firebase Console
   - Add your branding

3. **Test on Production**:
   - Set up environment variables on Render
   - Run migrations on production database
   - Test authentication on live site

4. **Mobile App Integration**:
   - Mobile apps already use same Firebase Auth
   - Users can login on both web and mobile

## Quick Commands Reference

```bash
# Run development server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check
```

## Important URLs

- **Home**: http://localhost:8000/
- **Login**: http://localhost:8000/giris/
- **Register**: http://localhost:8000/kayit/
- **Profile**: http://localhost:8000/profil/
- **Password Reset**: http://localhost:8000/sifre-sifirlama/
- **Admin**: http://localhost:8000/admin/

## Documentation

For complete documentation, see:
- `AUTHENTICATION_SETUP.md` - Full setup guide
- `IMPLEMENTATION_SUMMARY.md` - What was implemented
- `.env.example` - All environment variables

## Support

If you have issues:
1. Check `AUTHENTICATION_SETUP.md` troubleshooting section
2. Review Django logs in terminal
3. Check browser console for JavaScript errors
4. Verify Firebase Console settings

---

**You're all set!** The authentication system is ready to use.

Try creating an account and logging in at http://localhost:8000/kayit/
