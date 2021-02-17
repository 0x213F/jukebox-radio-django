from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from cryptography.fernet import Fernet


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
    spotify_scope = models.CharFiel(
        max_length=500, null=True, blank=True
    )
    idle_after_now_playing = models.BooleanField
    mute_voice_recordings = models.BooleanField
    focus_mode = models.BooleanField

    @property
    def spotify_access_token(self):
        if not self.encrypted_spotify_access_token:
            return None

        cipher_suite = Fernet(settings.FERNET_KEY)
        return cipher_suite.decrypt(
            self.encrypted_spotify_access_token.encode("utf-8")
        ).decode("utf-8")
