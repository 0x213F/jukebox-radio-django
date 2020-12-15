import uuid

from django.db import models

import pgtrigger


class QueueQuerySet(models.QuerySet):
    def in_stream(self, stream):
        """
        Get a list of all the queue items not yet played in a stream. Only root
        nodes of the queue tree are returned.
        """
        queue_qs = self.filter(
            stream=stream,
            played_at__isnull=True,
            deleted_at__isnull=True,
            is_abstract=False,
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
            initial_len = len(queue_list)

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

            if initial_len == len(queue_list):
                raise Exception("Infinite loop detected!")

        return sorted_queue_list


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
class Queue(models.Model):
    '''
    A queue is a piece of content (either a track or collection) selected to
    play in a stream. There are two important data structures used here.

      1: LINKED LIST - This is responsible for the order in which tracks are
                       played. Each of these is a child node of the tree
                       explained in 2: and points to a track, not a collection.
      2: TREE        - This is responsbile for the tree like structure to each
                       queued item. For example, when I queue up an album
                       (collection) it creates a queue item for the album and
                       for each track on the album. This allows the user to
                       remove either the album or individual tracks from the
                       queue.

    Non-abstract queues point to a track.

    Abstract queues point to a collection and must have children nodes. In the
    application logic, queue tree depth is limited to a 1. In the future, a
    recursive tree structure with unlimited depth is possible.
    '''

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

    start_at = models.PositiveIntegerField(null=True, blank=True)
    end_at = models.PositiveIntegerField(null=True, blank=True)

    play_with_stem_separation = models.BooleanField(default=False)
    play_bass_stem = models.BooleanField(null=True, blank=True)
    play_drums_stem = models.BooleanField(null=True, blank=True)
    play_vocals_stem = models.BooleanField(null=True, blank=True)
    play_other_stem = models.BooleanField(null=True, blank=True)

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

    played_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
