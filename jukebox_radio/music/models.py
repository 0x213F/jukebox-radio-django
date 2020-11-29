import pgtrigger
import uuid

from django.db import models

import pghistory
import pgtrigger
from unique_upload import unique_upload


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

    PROVIDER_SPOTIFY = "spotify"
    PROVIDER_YOUTUBE = "youtube"
    PROVIDER_JUKEBOX_RADIO = "jukebox_radio"
    PROVIDER_CHOICES = (
        (PROVIDER_SPOTIFY, "Spotify"),
        (PROVIDER_YOUTUBE, "YouTube"),
        (PROVIDER_JUKEBOX_RADIO, "Jukebox Radio"),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)

    name = models.CharField(max_length=200)
    duration_ms = models.PositiveIntegerField()

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
    FORMAT_MIX = "mix"
    FORMAT_CHOICES = (
        (FORMAT_ALBUM, "Album"),
        (FORMAT_PLAYLIST, "Playlist"),
        (FORMAT_MIX, "Mix"),
    )

    PROVIDER_SPOTIFY = "spotify"
    PROVIDER_YOUTUBE = "youtube"
    PROVIDER_JUKEBOX_RADIO = "jukebox_radio"
    PROVIDER_CHOICES = (
        (PROVIDER_SPOTIFY, "Spotify"),
        (PROVIDER_YOUTUBE, "YouTube"),
        (PROVIDER_JUKEBOX_RADIO, "Jukebox Radio"),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    format = models.CharField(max_length=32, choices=FORMAT_CHOICES)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)

    name = models.CharField(max_length=200)
    duration_ms = models.PositiveIntegerField()

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


# class Mix(Collection):
#     class Meta:
#         proxy = True
#         verbose_name = "Mix"
#         verbose_name_plural = "Mixes"
