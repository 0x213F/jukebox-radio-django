import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

import pghistory
import pgtrigger


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
@pghistory.track(pghistory.Snapshot("stream.snapshot"))
class Stream(models.Model):
    """
    Keeps track of playback. You could also think of this as a radio station.
    """

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

        now = timezone.now()
        within_bounds = self.paused_at - self.started_at < timedelta(
            milliseconds=self.now_playing.track.duration_ms
        )

        return within_bounds

    @property
    def now_playing_duration(self):
        if not self.now_playing_id or not self.now_playing.track_id:
            return None
        return timedelta(milliseconds=self.now_playing.track.duration_ms)
