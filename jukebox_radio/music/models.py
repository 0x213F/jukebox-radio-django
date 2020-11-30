import pgtrigger
import uuid

from django.db import models

import pghistory
import pgtrigger
from unique_upload import unique_upload


GLOBAL_PROVIDER_SPOTIFY = "spotify"
GLOBAL_PROVIDER_YOUTUBE = "youtube"
GLOBAL_PROVIDER_JUKEBOX_RADIO = "jukebox_radio"
GLOBAL_PROVIDER_CHOICES = (
    (GLOBAL_PROVIDER_SPOTIFY, "Spotify"),
    (GLOBAL_PROVIDER_YOUTUBE, "YouTube"),
    (GLOBAL_PROVIDER_JUKEBOX_RADIO, "Jukebox Radio"),
)


def upload_to_tracks_jr_audios(*args, **kwargs):
    return f"django-storage/music/tracks/jr-audios/" f"{unique_upload(*args, **kwargs)}"


def upload_to_tracks_jr_imgs(*args, **kwargs):
    return f"django-storage/music/tracks/jr-imgs/" f"{unique_upload(*args, **kwargs)}"


def upload_to_collections_jr_imgs(*args, **kwargs):
    return (
        f"django-storage/music/collections/jr-imgs/" f"{unique_upload(*args, **kwargs)}"
    )


@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class Track(models.Model):

    FORMAT_SONG = "song"
    FORMAT_VIDEO = "video"
    FORMAT_CHOICES = (
        (FORMAT_SONG, "Song"),
        (FORMAT_VIDEO, "Video"),
    )

    PROVIDER_SPOTIFY = GLOBAL_PROVIDER_SPOTIFY
    PROVIDER_YOUTUBE = GLOBAL_PROVIDER_YOUTUBE
    PROVIDER_JUKEBOX_RADIO = GLOBAL_PROVIDER_JUKEBOX_RADIO
    PROVIDER_CHOICES = GLOBAL_PROVIDER_CHOICES

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    format = models.CharField(max_length=32, choices=FORMAT_CHOICES)

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)

    name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    external_id = models.CharField(null=True, blank=True, max_length=200)
    audio = models.FileField(null=True, blank=True, upload_to=upload_to_tracks_jr_audios)

    img = models.ImageField(null=True, blank=True, upload_to=upload_to_tracks_jr_imgs)
    img_url = models.CharField(null=True, blank=True, max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class CollectionListing(models.Model):
    class Meta:
        unique_together = [
            "track",
            "collection",
            "number",
        ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    track = models.ForeignKey(
        "music.Track",
        on_delete=models.CASCADE,
    )
    collection = models.ForeignKey(
        "music.Collection",
        related_name="child_collection_listings",
        on_delete=models.CASCADE,
    )
    number = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)


@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class Collection(models.Model):

    FORMAT_ALBUM = "album"
    FORMAT_PLAYLIST = "playlist"
    FORMAT_SESSION = "session"
    FORMAT_CHOICES = (
        (FORMAT_ALBUM, "Album"),
        (FORMAT_PLAYLIST, "Playlist"),
        (FORMAT_SESSION, "Session"),
    )

    PROVIDER_SPOTIFY = GLOBAL_PROVIDER_SPOTIFY
    PROVIDER_YOUTUBE = GLOBAL_PROVIDER_YOUTUBE
    PROVIDER_JUKEBOX_RADIO = GLOBAL_PROVIDER_JUKEBOX_RADIO
    PROVIDER_CHOICES = GLOBAL_PROVIDER_CHOICES

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    format = models.CharField(max_length=32, choices=FORMAT_CHOICES)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)

    name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200, null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    external_id = models.CharField(null=True, max_length=200)

    img = models.ImageField(null=True, upload_to=upload_to_tracks_jr_imgs)
    img_url = models.CharField(null=True, max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Album(Collection):
    class Meta:
        proxy = True
        verbose_name = "Album"
        verbose_name_plural = "Albums"


class Playlist(Collection):
    class Meta:
        proxy = True
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"


class Session(Collection):
    class Meta:
        proxy = True
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
