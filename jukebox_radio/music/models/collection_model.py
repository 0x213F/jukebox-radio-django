import uuid

import pgtrigger
from django.apps import apps
from django.db import models
from unique_upload import unique_upload

from jukebox_radio.music.const import (
    GLOBAL_FORMAT_ALBUM,
    GLOBAL_FORMAT_PLAYLIST,
    GLOBAL_PROVIDER_APPLE_MUSIC,
    GLOBAL_PROVIDER_CHOICES,
    GLOBAL_PROVIDER_JUKEBOX_RADIO,
    GLOBAL_PROVIDER_SPOTIFY,
    GLOBAL_PROVIDER_YOUTUBE,
)


class CollectionManager(models.Manager):
    def serialize(self, collection):
        if not collection:
            return None

        return {
            "uuid": collection.uuid,
            "format": collection.format,
            "service": collection.provider,
            "name": collection.name,
            "artistName": collection.artist_name,
            "externalId": collection.external_id,
            "imageUrl": collection.img_url,
        }


def upload_to_collections_imgs(*args, **kwargs):
    return f"django-storage/music/collections/imgs/" f"{unique_upload(*args, **kwargs)}"


@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class Collection(models.Model):
    """
    Typically an album or a playlist, this model is a singular interface for
    all collections of tracks.
    """

    objects = CollectionManager()

    class Meta:
        unique_together = [
            "provider",
            "external_id",
        ]

    FORMAT_ALBUM = GLOBAL_FORMAT_ALBUM
    FORMAT_PLAYLIST = GLOBAL_FORMAT_PLAYLIST
    FORMAT_CHOICES = (
        (FORMAT_ALBUM, "Album"),
        (FORMAT_PLAYLIST, "Playlist"),
    )

    PROVIDER_APPLE_MUSIC = GLOBAL_PROVIDER_APPLE_MUSIC
    PROVIDER_SPOTIFY = GLOBAL_PROVIDER_SPOTIFY
    PROVIDER_YOUTUBE = GLOBAL_PROVIDER_YOUTUBE
    PROVIDER_JUKEBOX_RADIO = GLOBAL_PROVIDER_JUKEBOX_RADIO
    PROVIDER_CHOICES = GLOBAL_PROVIDER_CHOICES

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    format = models.CharField(max_length=32, choices=FORMAT_CHOICES)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)

    name = models.TextField()
    artist_name = models.TextField(null=True, blank=True)

    external_id = models.CharField(null=True, max_length=200)

    img = models.ImageField(null=True, upload_to=upload_to_collections_imgs)
    img_url = models.CharField(null=True, max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def list_tracks(self):
        CollectionListing = apps.get_model("music", "CollectionListing")
        Track = apps.get_model("music", "Track")
        track_uuids = (
            CollectionListing.objects.select_related("track")
            .filter(collection=self, deleted_at__isnull=True)
            .order_by("number")
            .values_list("track", flat=True)
        )
        tracks = list(Track.objects.filter(uuid__in=track_uuids))

        # sort the tracks according to CollectionListing values
        track_map = {}
        sorted_tracks = []
        for track in tracks:
            track_map[track.uuid] = track
        for track_uuid in track_uuids:
            sorted_tracks.append(track_map[track_uuid])

        return sorted_tracks

    @property
    def spotify_id(self):
        if not self.provider == self.PROVIDER_SPOTIFY:
            raise ValueError(f"Cannot read `spotify_id` of collection {self.uuid}")

        if self.format == self.FORMAT_ALBUM:
            return self.external_id[14:]
        elif self.format == self.FORMAT_PLAYLIST:
            return self.external_id[17:]
        else:
            raise ValueError(f"Unknown format of collection {self.uuid}")


class Album(Collection):
    """
    Proxy model for albums.
    """

    class Meta:
        proxy = True
        verbose_name = "Album"
        verbose_name_plural = "Albums"


class Playlist(Collection):
    """
    Proxy model for playlists.
    """

    class Meta:
        proxy = True
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"


@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_delete",
        operation=pgtrigger.Delete,
    )
)
class CollectionListing(models.Model):
    """
    This is the custom through table that keeps track of what tracks are in a
    collection as well as what order they go in.
    """

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

    # NOTE: it is possible for the tracks to change on an album/ playlist after
    #       it is initially created.
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"CollectionListing ({self.uuid})"
