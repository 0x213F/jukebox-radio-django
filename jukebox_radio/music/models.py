import pgtrigger

from django.db import models

import pghistory
import pgtrigger
from unique_upload import unique_upload


def upload_to_tracks_jr_audios(*args, **kwargs):
    return (
        f'django-storage/music/tracks/jr-audios/'
        f'{unique_upload(*args, **kwargs)}'
    )


def upload_to_tracks_jr_imgs(*args, **kwargs):
    return (
        f'django-storage/music/tracks/jr-imgs/'
        f'{unique_upload(*args, **kwargs)}'
    )


def upload_to_collections_jr_imgs(*args, **kwargs):
    return (
        f'django-storage/music/collections/jr-imgs/'
        f'{unique_upload(*args, **kwargs)}'
    )


@pgtrigger.register(
    pgtrigger.Protect(
        name='append_only',
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class Track(models.Model):

    # Jukebox Radio
    jr_audio = models.FileField(
        null=True,
        upload_to=upload_to_tracks_jr_audios,
    )
    jr_name = models.CharField(
        null=True,
        max_length=200,
    )
    jr_duration_ms = models.PositiveIntegerField(null=True)
    jr_img = models.ImageField(
        null=True,
        upload_to=upload_to_tracks_jr_imgs,
    )

    # Spotify
    spotify_uri = models.CharField(
        null=True,
        max_length=200,
    )
    spotify_name = models.CharField(
        null=True,
        max_length=200,
    )
    spotify_duration_ms = models.PositiveIntegerField(null=True)
    spotify_img = models.CharField(
        null=True,
        max_length=200,
    )

    # YouTube
    youtube_id = models.CharField(
        null=True,
        max_length=200,
    )
    youtube_name = models.CharField(
        null=True,
        max_length=200,
    )
    youtube_duration_ms = models.PositiveIntegerField(null=True)
    youtube_img = models.CharField(
        null=True,
        max_length=200,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jr_name or self.spotify_name or self.youtube_name


@pgtrigger.register(
    pgtrigger.Protect(
        name='append_only',
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class CollectionListing(models.Model):

    class Meta:
        unique_together = [
            "child_track",
            "child_collection",
            "parent_collection",
            "number",
        ]

    child_track = models.ForeignKey(
        'music.Track',
        on_delete=models.CASCADE,
    )
    child_collection = models.ForeignKey(
        'music.Collection',
        related_name='child_collection_listings',
        on_delete=models.CASCADE,
    )
    number = models.PositiveIntegerField()

    parent_collection = models.ForeignKey(
        'music.Collection',
        related_name='parent_collection_listings',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)


@pgtrigger.register(
    pgtrigger.Protect(
        name='append_only',
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class Collection(models.Model):

    FORMAT_ALBUM = 'album'
    FORMAT_PLAYLIST = 'playlist'
    FORMAT_MIX = 'mix'
    FORMAT_CHOICES = (
        (FORMAT_ALBUM, 'Album'),
        (FORMAT_PLAYLIST, 'Playlist'),
        (FORMAT_MIX, 'Mix'),
    )

    format = models.CharField(max_length=32, choices=FORMAT_CHOICES)

    # Jukebox Radio
    jr_name = models.CharField(
        null=True,
        max_length=128,
    )
    jr_duration_ms = models.PositiveIntegerField(null=True)
    jr_img = models.ImageField(
        null=True,
        upload_to=upload_to_collections_jr_imgs,
    )

    # Spotify
    spotify_uri = models.CharField(
        null=True,
        max_length=200,
    )
    spotify_name = models.CharField(
        null=True,
        max_length=200,
    )
    spotify_img = models.CharField(
        null=True,
        max_length=200,
    )

    # YouTube
    youtube_id = models.CharField(
        null=True,
        max_length=200,
    )
    youtube_name = models.CharField(
        null=True,
        max_length=200,
    )
    youtube_img = models.CharField(
        null=True,
        max_length=200,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jr_name or self.spotify_name or self.youtube_name


class Album(Collection):
    class Meta:
        proxy = True
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'


class Playlist(Collection):
    class Meta:
        proxy = True
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'


class Mix(Collection):
    class Meta:
        proxy = True
        verbose_name = 'Mix'
        verbose_name_plural = 'Mixes'
