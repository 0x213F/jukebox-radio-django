import uuid

from django.db import models

import pgtrigger


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
class QueueInterval(models.Model):
    """
    An interval of a queue item (tracks only, not collections). When that queue
    item is played, the interval defined by the bounds will be omitted from
    playback.

    The bounds are represented by Marker objects. If the lower bound marker is
    None, it represents the beginning of the track. If the upper bound marker
    is None, it represents the end of the track.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    queue = models.ForeignKey(
        "streams.Queue",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )

    lower_bound = models.ForeignKey(
        "streams.Marker",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )
    upper_bound = models.ForeignKey(
        "streams.Marker",
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
    )

    is_muted = models.BooleanField()
    repeat_count = models.PositiveSmallIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
