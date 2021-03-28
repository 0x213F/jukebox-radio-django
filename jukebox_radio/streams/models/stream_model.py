import uuid
from datetime import timedelta

import pghistory
import pgtrigger
from django.apps import apps
from django.db import models
from django.db.models import Exists, OuterRef, Subquery
from django.utils import timezone

from jukebox_radio.core import time as time_util
from jukebox_radio.music.refresh import refresh_track_external_data


class StreamManager(models.Manager):
    def serialize(self, stream):
        Queue = apps.get_model("streams", "Queue")
        return {
            "uuid": stream.uuid,
            "nowPlaying": Queue.objects.serialize(stream.now_playing),
            "isPlaying": stream.is_playing,
            "isPaused": stream.is_paused,
            "startedAt": time_util.epoch(stream.started_at),
            "pausedAt": time_util.epoch(stream.paused_at),
        }


class StreamQuerySet(models.QuerySet):
    def filter_idle(self):
        """
        Filters to streams which are idle.
        """
        Queue = apps.get_model("streams", "Queue")

        now = time_util.now()
        three_hours_ago = now - timedelta(hours=3)

        newest_queue_track_id = (
            Queue.objects.filter(
                stream_id=OuterRef("uuid"),
                deleted_at__isnull=True,
            )
            .order_by("-index")
            .values_list("track_id", flat=True)[:1]
        )

        newest_queue_collection_id = (
            Queue.objects.filter(
                stream_id=OuterRef("uuid"),
                deleted_at__isnull=True,
            )
            .order_by("-index")
            .values_list("collection_id", flat=True)[:1]
        )

        return (
            self.annotate(
                newest_queue_track_id=Subquery(newest_queue_track_id),
            )
            .annotate(
                newest_queue_collection_id=Subquery(newest_queue_collection_id),
            )
            .filter(
                # No recently played queues == streams that are idle.
                ~Exists(
                    Queue.objects.filter(stream_id=OuterRef("uuid")).exclude(
                        played_at__lte=three_hours_ago
                    )
                )
            )
            .exclude(
                newest_queue_track_id__isnull=True,
                newest_queue_collection_id__isnull=True,
            )
        )


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
@pghistory.track(pghistory.Snapshot("stream.snapshot"))
class Stream(models.Model):
    """
    Keeps track of playback. You could also think of this as a radio station.
    """

    objects = StreamManager.from_queryset(StreamQuerySet)()

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    now_playing = models.ForeignKey(
        "streams.Queue",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)

    recording_started_at = models.DateTimeField(null=True, blank=True)
    recording_ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_playing(self):
        is_playing = bool(self.started_at)
        if not is_playing or not self.now_playing_id or not self.now_playing.track_id:
            return False

        is_paused = bool(self.paused_at)
        if is_paused and self.paused_at > self.started_at:
            return False

        duration = self.now_playing.track.duration_ms
        if not duration:
            track = duration = self.now_playing.track
            user = self.user
            refresh_track_external_data(track, user)

        now = timezone.now()
        within_bounds = now < self.started_at + timedelta(
            milliseconds=self.now_playing.track.duration_ms
        )

        return within_bounds

    @property
    def is_paused(self):
        is_paused = bool(self.paused_at)
        if not is_paused or not self.now_playing_id or not self.now_playing.track_id:
            return False

        is_playing = bool(self.started_at)
        if is_playing and self.started_at > self.paused_at:
            return False

        within_bounds = self.paused_at - self.started_at < timedelta(
            milliseconds=self.now_playing.track.duration_ms
        )

        return within_bounds

    def controls_enabled(self, end_buffer, total_duration):
        """
        A stream's playback controls are disabled towards the end of the now
        playing track. This determines if the stream is able to have the
        controls enabled or not.
        """
        track_ends_at = self.started_at + total_duration
        now = time_util.now()
        return now + end_buffer < track_ends_at

    @property
    def now_playing_duration(self):
        """
        WARNING - this is not accurate. The duration for now playing is more
        complicated than this. It must take into consideration the intervals.

        NOTE - for now, the calculation for the duration of now playing (or any
        queue item) is done on the front-end. Yes, that is not ideal, but it
        seemingly works for the time being.
        """
        if not self.now_playing_id or not self.now_playing.track_id:
            return None
        return timedelta(milliseconds=self.now_playing.track.duration_ms)
