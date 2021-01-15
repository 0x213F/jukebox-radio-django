import uuid

from django.apps import apps
from django.db import models
from django.db import transaction
from django.db.models import Prefetch
from django.db.models import F

import pgtrigger


@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class Marker(models.Model):
    """
    A bookmark to a book is like a marker to a track. A user may set markers on
    a track to indicate points of interest. For example, you might want to set
    a marker at the beginning of a solo.
    """
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
