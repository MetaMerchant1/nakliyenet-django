"""
Context processors - Tüm template'lerde kullanılabilir değişkenler
"""
from django.conf import settings
import os


def site_settings(request):
    """Site genelinde kullanılacak ayarlar"""
    # Firebase configuration for frontend
    firebase_config = {
        'apiKey': os.getenv('FIREBASE_API_KEY', ''),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': os.getenv('FIREBASE_PROJECT_ID', ''),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', ''),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': os.getenv('FIREBASE_APP_ID', ''),
    }

    return {
        'SITE_URL': settings.SITE_URL,
        'IOS_APP_URL': settings.IOS_APP_URL,
        'ANDROID_APP_URL': settings.ANDROID_APP_URL,
        'SITE_NAME': 'NAKLIYE NET',
        'SITE_DESCRIPTION': 'Türkiye\'nin Dijital Yük Pazaryeri',
        'FIREBASE_API_KEY': firebase_config['apiKey'],
        'FIREBASE_AUTH_DOMAIN': firebase_config['authDomain'],
        'FIREBASE_PROJECT_ID': firebase_config['projectId'],
        'FIREBASE_STORAGE_BUCKET': firebase_config['storageBucket'],
        'FIREBASE_MESSAGING_SENDER_ID': firebase_config['messagingSenderId'],
        'FIREBASE_APP_ID': firebase_config['appId'],
    }
