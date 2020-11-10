from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Default user for Jukebox Radio.
    """

    encrypted_spotify_access_token = models.CharField(max_length=500, null=True, blank=True)
    encrypted_spotify_refresh_token = models.CharField(max_length=500, null=True, blank=True)
    spotify_scope = models.CharField(max_length=500, null=True, blank=True)
