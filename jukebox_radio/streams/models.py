import pgtrigger
import uuid

from django.db import models

import pghistory
import pgtrigger
from unique_upload import unique_upload


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
@pghistory.track(pghistory.Snapshot("stream.snapshot"))
class Stream(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    now_playing = models.ForeignKey("music.Track", on_delete=models.CASCADE, null=True, blank=True)
    played_at = models.DateTimeField(null=True, blank=True)
    is_playing = models.BooleanField(default=False)

    recording_started_at = models.DateTimeField(null=True, blank=True)
    recording_ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
class Queue(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    track = models.ForeignKey(
        "music.Track",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )
    collection = models.ForeignKey(
        "music.Collection",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )

    stream = models.ForeignKey(
        "streams.Stream",
        related_name="+",
        on_delete=models.CASCADE,
    )
    prev_queue_ptr = models.ForeignKey(
        "streams.Queue",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )
    next_queue_ptr = models.ForeignKey(
        "streams.Queue",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )

    is_abstract = models.BooleanField()
    parent_queue_ptr = models.ForeignKey(
        "streams.Queue",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )

    played_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
