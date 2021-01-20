import uuid

from django.apps import apps
from django.db import models
from django.db.models import Q

import pgtrigger


class QueueIntervalManager(models.Manager):
    def serialize(self, queue_interval):
        return {}

    def create_queue_interval(
        self, *, user, queue_id, lower_bound_id, upper_bound_id, is_muted,
        repeat_count,
    ):
        QueueInterval = apps.get_model('streams', 'QueueInterval')

        if not lower_bound_id and not upper_bound_id:
            raise ValueError("Either lower or upper must be specified")

        lowest_bound = QueueInterval.objects.lowest_bound(queue_id)
        if not lower_bound_id and lowest_bound.exists():
            raise ValueError("A conflicting QueueInterval already exists")

        highest_bound = QueueInterval.objects.highest_bound(queue_id)
        if not upper_bound_id and highest_bound.exists():
            raise ValueError("A conflicting QueueInterval already exists")

        if lower_bound_id and upper_bound_id:
            conflicting_interval = (
                QueueInterval
                .objects
                .conflicting_interval(
                    queue_id=queue_id,
                    lower_bound_id=lower_bound_id,
                    upper_bound_id=upper_bound_id,
                )
            )
            if conflicting_interval.exists():
                raise ValueError("A conflicting QueueInterval already exists")

        return QueueInterval.objects.create(
            user=user,
            queue_id=queue_id,
            lower_bound_id=lower_bound_id,
            upper_bound_id=upper_bound_id,
            is_muted=is_muted,
            repeat_count=repeat_count,
        )



class QueueIntervalQuerySet(models.QuerySet):
    def lowest_bound(self, queue_id):
        return self.filter(
            queue_id=queue_id,
            lower_bound__isnull=True,
        )

    def highest_bound(self, queue_id):
        return self.filter(
            queue_id=queue_id,
            upper_bound__isnull=True,
        )

    def conflicting_interval(self, *, queue_id, lower_bound_id, upper_bound_id):
        Marker = apps.get_model('streams', 'Marker')

        lower_bound = Marker.objects.get(uuid=lower_bound_id, queue_id=queue_id)
        upper_bound = Marker.objects.get(uuid=upper_bound_id, queue_id=queue_id)

        return self.filter(
            Q(
                Q(
                    queue_id=queue_id,
                    lower_bound__timestamp_ms__lt=upper_bound.timestamp_ms,
                    lower_bound__timestamp_ms__gt=lower_bound.timestamp_ms,
                ) |
                Q(
                    queue_id=queue_id,
                    upper_bound__timestamp_ms__gt=lower_bound.timestamp_ms,
                    upper_bound__timestamp_ms__lt=upper_bound.timestamp_ms,
                )
            )
        )


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
    objects = QueueIntervalManager.from_queryset(QueueIntervalQuerySet)()

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
    repeat_count = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
