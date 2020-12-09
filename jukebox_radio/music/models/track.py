import uuid

from django.db import models

import pgtrigger
from unique_upload import unique_upload

from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_SPOTIFY
from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_YOUTUBE
from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_JUKEBOX_RADIO
from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_CHOICES


def upload_to_tracks_jr_audios(*args, **kwargs):
    return f"django-storage/music/tracks/jr-audios/" f"{unique_upload(*args, **kwargs)}"


def upload_to_tracks_jr_imgs(*args, **kwargs):
    return f"django-storage/music/tracks/jr-imgs/" f"{unique_upload(*args, **kwargs)}"


@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_delete",
        operation=pgtrigger.Delete,
    )
)
class Track(models.Model):
    class Meta:
        unique_together = [
            "provider",
            "external_id",
        ]

    FORMAT_TRACK = "track"
    FORMAT_VIDEO = "video"
    FORMAT_CHOICES = (
        (FORMAT_TRACK, "Track"),
        (FORMAT_VIDEO, "Video"),
    )

    PROVIDER_SPOTIFY = GLOBAL_PROVIDER_SPOTIFY
    PROVIDER_YOUTUBE = GLOBAL_PROVIDER_YOUTUBE
    PROVIDER_JUKEBOX_RADIO = GLOBAL_PROVIDER_JUKEBOX_RADIO
    PROVIDER_CHOICES = GLOBAL_PROVIDER_CHOICES

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )

    format = models.CharField(max_length=32, choices=FORMAT_CHOICES)

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)

    name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    album_name = models.CharField(max_length=200)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    audio = models.FileField(
        null=True, blank=True, upload_to=upload_to_tracks_jr_audios
    )
    external_id = models.CharField(null=True, blank=True, max_length=200)

    img = models.ImageField(null=True, blank=True, upload_to=upload_to_tracks_jr_imgs)
    img_url = models.CharField(null=True, blank=True, max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def spotify_id(self):
        if not self.provider == self.PROVIDER_SPOTIFY:
            raise ValueError(f"Cannot read `spotify_id` of track {self.uuid}")
        return self.external_id[14:]

    @property
    def youtube_id(self):
        if not self.provider == self.PROVIDER_YOUTUBE:
            raise ValueError(f"Cannot read `youtube_id` of track {self.uuid}")
        return self.external_id