import uuid

from django.db import models

import pgtrigger
from unique_upload import unique_upload

from jukebox_radio.music.const import GLOBAL_PROVIDER_SPOTIFY
from jukebox_radio.music.const import GLOBAL_PROVIDER_YOUTUBE
from jukebox_radio.music.const import GLOBAL_PROVIDER_JUKEBOX_RADIO
from jukebox_radio.music.const import GLOBAL_PROVIDER_CHOICES


class TrackManager(models.Manager):

    def serialize(self, track):
        if not track:
            return None

        return {
            "uuid": track.uuid,
            "format": track.format,
            "service": track.provider,
            "name": track.name,
            "artistName": track.artist_name,
            "albumName": track.album_name,
            "durationMilliseconds": track.duration_ms,
            "externalId": track.external_id,
            "imageUrl": track.img_url,
        }


def upload_to_tracks_audios(*args, **kwargs):
    return f"django-storage/music/tracks/audios/" f"{unique_upload(*args, **kwargs)}"


def upload_to_tracks_imgs(*args, **kwargs):
    return f"django-storage/music/tracks/imgs/" f"{unique_upload(*args, **kwargs)}"


@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_delete",
        operation=pgtrigger.Delete,
    )
)
class Track(models.Model):
    """
    A singular piece of streamable media. All queue root nodes point to tracks.
    """

    objects = TrackManager()

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

    name = models.TextField()
    artist_name = models.TextField()
    album_name = models.TextField()
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    audio = models.FileField(null=True, blank=True, upload_to=upload_to_tracks_audios)
    external_id = models.CharField(null=True, blank=True, max_length=200)

    img = models.ImageField(null=True, blank=True, upload_to=upload_to_tracks_imgs)
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
