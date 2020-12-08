import pgtrigger
import uuid

from django.db import models

import pghistory
import pgtrigger
from unique_upload import unique_upload


def upload_to_comments_voice_recordings(*args, **kwargs):
    return (
        f"django-storage/comments/voice-recordings/audios/"
        f"{unique_upload(*args, **kwargs)}"
    )


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
@pghistory.track(pghistory.Snapshot("text_comment.snapshot"))
class TextComment(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    text = models.TextField()
    track = models.ForeignKey("music.Track", on_delete=models.CASCADE)
    timestamp_ms = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.user}] {self.text}"


@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class VoiceRecording(models.Model):

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


@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class TextCommentModification(models.Model):

    STYLE_HIGHLIGHT = "highlight"
    STYLE_STRIKETHROUGH = "strikethrough"
    STYLE_UNDERLINE = "underline"
    STYLE_CHOICES = (
        (STYLE_HIGHLIGHT, "Highlight"),
        (STYLE_STRIKETHROUGH, "Strikethrough"),
        (STYLE_UNDERLINE, "Underline"),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    text_comment = models.ForeignKey(
        "comments.TextComment",
        on_delete=models.CASCADE,
    )

    start_ptr = models.PositiveSmallIntegerField()
    end_ptr = models.PositiveSmallIntegerField()
    style = models.CharField(max_length=32, choices=STYLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.text_comment} ({self.start_ptr}, {self.end_ptr})"
