from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

from cryptography.fernet import Fernet

def upload_to_profile_imgs(*args, **kwargs):
    return f"django-storage/users/user-profile/profile-imgs/{unique_upload(*args, **kwargs)}"

class UserProfile(models.Model):
    """
    User Profile
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(
        null=True, blank=True, upload_to=upload_to_profile_imgs
    )
    description = models.TextField(
        max_length=500, null=True, blank=True
    )
    website = models.URLField(null=True, blank=True)

class User(AbstractUser):
    """
    Default user for Jukebox Radio.
    """

    encrypted_spotify_access_token = models.CharField(
        max_length=500, null=True, blank=True
    )
    encrypted_spotify_refresh_token = models.CharField(
        max_length=500, null=True, blank=True
    )
    spotify_scope = models.CharField(max_length=500, null=True, blank=True)
    idle_after_now_playing = models.BooleanField(default=False)
    mute_voice_recordings = models.BooleanField(default=True)
    focus_mode = models.BooleanField(default=False)

    @property
    def spotify_access_token(self):
        if not self.encrypted_spotify_access_token:
            return None

        cipher_suite = Fernet(settings.FERNET_KEY)
        return cipher_suite.decrypt(
            self.encrypted_spotify_access_token.encode("utf-8")
        ).decode("utf-8")

