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

    now_playing = models.ForeignKey(
        "music.Track", on_delete=models.CASCADE, null=True, blank=True
    )
    played_at = models.DateTimeField(null=True, blank=True)
    is_playing = models.BooleanField(default=False)

    recording_started_at = models.DateTimeField(null=True, blank=True)
    recording_ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class QueueQuerySet(models.QuerySet):
    def in_stream(self, stream):
        queue_qs = self.filter(
            stream=stream,
            played_at__isnull=True,
            deleted_at__isnull=True,
        )

        queue_list = list(queue_qs)
        if not queue_list:
            return []

        # Fun stuff here. We need to iron out our queryset into a sorted list.
        # Since this is a doubly-linked-list, I don't think it is possible to
        # do this inside the Django ORM. This sorts in O(N^2)
        sorted_queue_list = [queue_list[0]]
        del queue_list[0]

        while queue_list:
            for idx in range(len(queue_list)):
                queue = queue_list[idx]

                if queue == sorted_queue_list[-1].next_queue_ptr:
                    sorted_queue_list.append(queue)
                    del queue_list[idx]
                    break

                if queue == sorted_queue_list[0].prev_queue_ptr:
                    sorted_queue_list.insert(0, queue)
                    del queue_list[idx]
                    break

        return sorted_queue_list

@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
class Queue(models.Model):

    objects = QueueQuerySet.as_manager()

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

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

    is_head = models.BooleanField(default=False)
    is_tail = models.BooleanField(default=False)

    played_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
