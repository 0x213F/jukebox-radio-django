import uuid

import pgtrigger
from django.db import models

from jukebox_radio.core import time as time_util


class MarkerManager(models.Manager):
    def serialize(self, marker):
        if not marker:
            return None

        return {
            "uuid": marker.uuid,
            "trackUuid": marker.track_id,
            "timestampMilliseconds": marker.timestamp_ms,
        }


class MarkerQuerySet(models.QuerySet):
    def filter_by_track_and_user(self, track_uuid, user):
        return self.filter(
            user=user,
            track_id=track_uuid,
            deleted_at__isnull=True,
        ).order_by("timestamp_ms")


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
class Marker(models.Model):
    """
    A bookmark to a book is like a marker to a track. A user may set markers on
    a track to indicate points of interest. For example, you might want to set
    a marker at the beginning of a solo.
    """

    objects = MarkerManager.from_queryset(MarkerQuerySet)()

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    track = models.ForeignKey(
        "music.Track",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )

    timestamp_ms = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def archive(self):
        self.deleted_at = time_util.now()
        self.save()
