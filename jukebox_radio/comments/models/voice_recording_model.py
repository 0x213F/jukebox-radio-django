import pgtrigger
import uuid

from django.db import models

import pghistory
import pgtrigger
from unique_upload import unique_upload

from jukebox_radio.core import time as time_util


def upload_to_comments_voice_recordings(*args, **kwargs):
    return (
        f"django-storage/comments/voice-recordings/audios/"
        f"{unique_upload(*args, **kwargs)}"
    )


class VoiceRecordingManager(models.Manager):
    def serialize(self, voice_recording):
        return {
            "class": voice_recording.__class__.__name__,
            "uuid": voice_recording.uuid,
            "user": voice_recording.user.username,
            "transcriptData": voice_recording.transcript_data,
            "transcriptFinal": voice_recording.transcript_final,
            "durationMilliseconds": voice_recording.duration_ms,
            "trackUuid": voice_recording.track_id,
            "timestampMilliseconds": voice_recording.timestamp_ms,
        }


class VoiceRecordingQuerySet(models.QuerySet):
    def notepad_filter(self, track_uuid, user):
        return (
            self.objects.select_related("user", "track")
            .filter(track__uuid=track_uuid, user=user, deleted_at__isnull=True)
            .order_by("timestamp_ms")
        )


@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_deletes",
        operation=pgtrigger.Delete,
    )
)
@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_updates",
        operation=pgtrigger.Update,
    )
)
class VoiceRecording(models.Model):

    objects = VoiceRecordingManager.from_queryset(VoiceRecordingQuerySet)()

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    audio = models.FileField(upload_to=upload_to_comments_voice_recordings)
    transcript_data = models.JSONField()
    transcript_final = models.TextField(null=True)
    duration_ms = models.IntegerField()
    track = models.ForeignKey("music.Track", on_delete=models.CASCADE)
    timestamp_ms = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.user}] {self.duration_ms / 1000}s voice recording"

    @pgtrigger.ignore("comments.VoiceRecording:protect_updates")
    def archive(self):
        self.deleted_at = time_util.now()
        self.save()
