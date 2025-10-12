"""
Signals for automatic UserProfile creation when users login via Google OAuth
"""
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from allauth.socialaccount.signals import pre_social_login
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when a new User is created
    """
    if created:
        try:
            UserProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'user_type': 0,  # Default: Shipper
                }
            )
            logger.info(f"Created UserProfile for user: {instance.email}")
        except Exception as e:
            logger.error(f"Error creating UserProfile: {e}", exc_info=True)


@receiver(pre_social_login)
def link_social_account(sender, request, sociallogin, **kwargs):
    """
    When user logs in with Google OAuth, ensure UserProfile exists
    """
    try:
        # If user is being created, UserProfile will be created by post_save signal
        if sociallogin.is_existing:
            # Existing user - ensure profile exists
            user = sociallogin.user
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': 0,
                }
            )
            logger.info(f"Ensured UserProfile exists for: {user.email}")
    except Exception as e:
        logger.error(f"Error in social login signal: {e}", exc_info=True)
