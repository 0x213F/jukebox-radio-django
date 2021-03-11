import uuid

import pgtrigger
from django.apps import apps
from django.db import models
from django.db.models import Q

from jukebox_radio.core import time as time_util


class QueueIntervalManager(models.Manager):
    def serialize(self, queue_interval):
        Marker = apps.get_model("streams", "Marker")
        return {
            "uuid": queue_interval.uuid,
            "queueUuid": queue_interval.queue_id,
            "lowerBound": Marker.objects.serialize(queue_interval.lower_bound),
            "upperBound": Marker.objects.serialize(queue_interval.upper_bound),
            "purpose": queue_interval.purpose,
        }

    def create_queue_interval(
        self,
        *,
        user,
        queue_id,
        lower_bound_id,
        upper_bound_id,
        purpose,
    ):
        QueueInterval = apps.get_model("streams", "QueueInterval")

        if not lower_bound_id and not upper_bound_id:
            raise ValueError("Either lower or upper must be specified")

        elif not lower_bound_id and upper_bound_id:
            conflicting_lowest_bound = QueueInterval.objects.conflicting_lowest_bound(
                queue_id, upper_bound_id
            )
            if conflicting_lowest_bound:
                raise ValueError("A conflicting QueueInterval already exists")

        elif lower_bound_id and not upper_bound_id:
            conflicting_highest_bound = QueueInterval.objects.conflicting_highest_bound(
                queue_id, lower_bound_id
            )
            if conflicting_highest_bound:
                raise ValueError("A conflicting QueueInterval already exists")

        else:  # lower_bound_id and upper_bound_id:
            conflicting_interval = QueueInterval.objects.conflicting_interval(
                queue_id=queue_id,
                lower_bound_id=lower_bound_id,
                upper_bound_id=upper_bound_id,
            )
            if conflicting_interval:
                raise ValueError("A conflicting QueueInterval already exists")

        return QueueInterval.objects.create(
            user=user,
            queue_id=queue_id,
            lower_bound_id=lower_bound_id,
            upper_bound_id=upper_bound_id,
            purpose=purpose,
        )


class QueueIntervalQuerySet(models.QuerySet):
    def conflicting_lowest_bound(self, queue_id, upper_bound_id):
        """
        This method is called before creating a new queue interval that has
        no lower bound (meaning the bounds go from the beginning of the track
        to the upper bound). It returns a boolean signifying wether there is a
        conflict.
          - True: there is a conflict - DO NOT create queue interval.
          - False: there is no conflict - ok to create queue interval.
        """
        Marker = apps.get_model("streams", "Marker")
        QueueInterval = apps.get_model("streams", "QueueInterval")

        conflict = QueueInterval.objects.filter(
            queue_id=queue_id,
            lower_bound__isnull=True,
            deleted_at__isnull=True,
        ).exists()
        if conflict:
            return True

        proposed_upper_bound = Marker.objects.get(uuid=upper_bound_id)
        lowest_interval = (
            QueueInterval.objects.select_related("lower_bound")
            .filter(
                queue_id=queue_id,
                deleted_at__isnull=True,
            )
            .order_by("lower_bound__timestamp_ms")
            .first()
        )

        if not lowest_interval:
            return False

        upper_bound_limit = lowest_interval.lower_bound.timestamp_ms
        if proposed_upper_bound.timestamp_ms > upper_bound_limit:
            return True

        return False

    def conflicting_highest_bound(self, queue_id, lower_bound_id):
        """
        This method is called before creating a new queue interval that has
        no upper bound (meaning the bounds go from the lower bound to the end
        of the track). It returns a boolean signifying wether there is a
        conflict.
          - True: there is a conflict - DO NOT create queue interval.
          - False: there is no conflict - ok to create queue interval.
        """
        Marker = apps.get_model("streams", "Marker")
        QueueInterval = apps.get_model("streams", "QueueInterval")

        conflict = QueueInterval.objects.filter(
            queue_id=queue_id,
            upper_bound__isnull=True,
            deleted_at__isnull=True,
        ).exists()
        if conflict:
            return True

        proposed_lower_bound = Marker.objects.get(uuid=lower_bound_id)
        highest_interval = (
            QueueInterval.objects.select_related("upper_bound")
            .filter(
                queue_id=queue_id,
                deleted_at__isnull=True,
            )
            .order_by("upper_bound__timestamp_ms")
            .last()
        )

        if not highest_interval:
            return False

        lower_bound_limit = highest_interval.upper_bound.timestamp_ms
        if proposed_lower_bound.timestamp_ms < lower_bound_limit:
            return True

        return False

    def conflicting_interval(self, *, queue_id, lower_bound_id, upper_bound_id):
        """
        This method is called before creating a new queue interval between two
        given bounds. It returns a boolean signifying wether there is a
        conflict.
          - True: there is a conflict - DO NOT create queue interval.
          - False: there is no conflict - ok to create queue interval.
        """
        Marker = apps.get_model("streams", "Marker")
        Queue = apps.get_model("streams", "Queue")
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue = Queue.objects.select_related("track").get(uuid=queue_id)
        track = queue.track

        lower_bound = Marker.objects.get(uuid=lower_bound_id, track=track)
        upper_bound = Marker.objects.get(uuid=upper_bound_id, track=track)

        return QueueInterval.objects.filter(
            Q(
                Q(
                    queue_id=queue_id,
                    lower_bound__timestamp_ms__lt=upper_bound.timestamp_ms,
                    lower_bound__timestamp_ms__gt=lower_bound.timestamp_ms,
                    deleted_at__isnull=True,
                )
                | Q(
                    queue_id=queue_id,
                    upper_bound__timestamp_ms__gt=lower_bound.timestamp_ms,
                    upper_bound__timestamp_ms__lt=upper_bound.timestamp_ms,
                    deleted_at__isnull=True,
                )
                | Q(
                    queue_id=queue_id,
                    lower_bound__timestamp_ms=lower_bound.timestamp_ms,
                    upper_bound__timestamp_ms=upper_bound.timestamp_ms,
                    deleted_at__isnull=True,
                )
            )
        ).exists()


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

    PURPOSE_MUTED = "muted"
    PURPOSE_SOLO_DRUMS = "solo_drums"
    PURPOSE_SOLO_VOCALS = "solo_vocals"
    PURPOSE_SOLO_BASS = "solo_bass"
    PURPOSE_SOLO_OTHER = "solo_other"

    PURPOSE_CHOICES = [
        (PURPOSE_MUTED, "Muted"),
        (PURPOSE_SOLO_DRUMS, "Solo drums"),
        (PURPOSE_SOLO_VOCALS, "Solo vocals"),
        (PURPOSE_SOLO_BASS, "Solo bass"),
        (PURPOSE_SOLO_OTHER, "Solo other"),
    ]

    objects = QueueIntervalManager.from_queryset(QueueIntervalQuerySet)()

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    queue = models.ForeignKey(
        "streams.Queue",
        related_name="intervals",
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

    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def archive(self):
        self.deleted_at = time_util.now()
        self.save()
