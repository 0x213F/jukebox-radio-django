import uuid

from django.apps import apps
from django.db import models
from django.db import transaction
from django.db.models import Prefetch
from django.db.models import F

import pgtrigger


class QueueManager(models.Manager):
    def serialize(self, queue, is_child=False):
        Collection = apps.get_model("music", "Collection")
        Track = apps.get_model("music", "Track")
        QueueInterval = apps.get_model("streams", "QueueInterval")

        if not queue:
            return None

        track = Track.objects.serialize(queue.track) if queue.track_id else None
        collection = Collection.objects.serialize(queue.collection) if queue.collection_id else None

        obj = {
            "uuid": queue.uuid,
            "index": queue.index,
            "track": track,
            "collection": collection,
            "parentUuid": queue.parent_id,
            "isAbstract": queue.is_abstract,
            "isArchived": bool(queue.deleted_at),
        }

        try:
            queue_children = queue.ordered_children
        except AttributeError:
            queue_children = []
        children = []
        for child in queue_children:
            children.append(self.serialize(child, is_child=True))
        obj["children"] = children

        try:
            active_intervals = queue.active_intervals
        except AttributeError:
            active_intervals = []
        intervals = []
        for interval in active_intervals:
            intervals.append(QueueInterval.objects.serialize(interval))
        obj["intervals"] = intervals

        return obj

    @pgtrigger.ignore("streams.Queue:protect_inserts")
    def create_initial_queue(self, stream):
        """
        Custom create method
        """
        Queue = apps.get_model("streams", "Queue")

        return Queue.objects.create(
            stream=stream,
            user=stream.user,
            index=Queue.INITIAL_INDEX,
            is_head=True,
            is_abstract=False,
        )

    @pgtrigger.ignore("streams.Queue:protect_inserts")
    def create_queue(
        self, index=None, stream=None, track=None, collection=None, user=None, **kwargs
    ):
        """
        Custom create method
        """
        Queue = apps.get_model("streams", "Queue")

        if not index:
            last_queue = Queue.objects.last_queue(stream)
            index = last_queue.index + 1

        queue_head = Queue.objects.get_head(stream)
        if queue_head.index >= index:
            raise ValueError("Index value is too small")

        # NOTE: This is a little hacky. We calculate the offset that in queue
        #       indexes need to be bumped up by.
        _tracks = collection.list_tracks() if collection else [None]
        if not len(_tracks):
            raise ValueError(f"Collection has no tracks: {collection.uuid}")
        offset = len(_tracks)

        with transaction.atomic():
            next_up_tracks_only = Queue.objects.filter(
                index__gte=index,
                stream=stream,
                deleted_at__isnull=True,
            )
            next_up_tracks_only.update(index=F("index") + offset)

            queues = []

            parent_queue = (
                Queue(
                    stream=stream,
                    index=(index + offset - 1),
                    user=user,
                    collection=collection,
                    is_abstract=True,
                )
                if collection
                else None
            )
            if parent_queue:
                queues.append(parent_queue)

            for _track in _tracks:
                queue = Queue(
                    stream=stream,
                    index=index,
                    user=user,
                    track=(_track or track),
                    collection=collection,
                    is_abstract=False,
                    parent=parent_queue,
                )
                queues.append(queue)
                index += 1

            Queue.objects.bulk_create(queues)


class QueueQuerySet(models.QuerySet):
    def prefetch_active_intervals(self):
        """
        Simple prefetch of queue intervals. This is needed because the deleted
        (archived) intervals should not be included in the query.

        We also join the bounds using select related since they are needed in
        context of the queue intervals.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        return self.prefetch_related(
            Prefetch(
                "intervals",
                queryset=(
                    QueueInterval.objects
                    .select_related("lower_bound", "upper_bound")
                    .filter(
                        deleted_at__isnull=True
                    )
                ),
                to_attr="active_intervals",
            )
        )

    def last_queue(self, stream):
        """
        This gets the very last item in a stream's queue.
        """
        return self.filter(
            stream=stream, deleted_at__isnull=True, is_abstract=False
        ).order_by("-index")[0]

    def get_head(self, stream):
        """
        This gets the current head of the queue, aka "now playing." Currently
        there are 3 ways to query for this value.

        - The smart way: the queue with the most recent value for "played_at"
        - The convenient way: "stream.now_playing"
        - The explicit way: query on "is_head"

        This does not seem ideal. Perhaps "is_head" could be deprecated in the
        future?
        """
        head = Queue.objects.get(stream=stream, is_head=True, deleted_at__isnull=True)
        if stream.now_playing_id != head.uuid:
            raise ValueError('Unexpected head')
        return head

    def get_prev(self, stream):
        """
        Get the queue item directly BEFORE the current head.
        """
        head = Queue.objects.get_head(stream)
        try:
            return Queue.objects.get(
                stream=stream,
                index=(head.index - 1),
                is_abstract=False,
                deleted_at__isnull=True,
            )
        except Queue.DoesNotExist:
            return None

    def get_next(self, stream):
        """
        Get the queue item directly AFTER the current head.
        """
        head = Queue.objects.get_head(stream)
        try:
            return Queue.objects.get(
                stream=stream,
                index=(head.index + 1),
                is_abstract=False,
                deleted_at__isnull=True,
            )
        except Queue.DoesNotExist:
            return None

    def next_up_tracks_only(self, stream):
        """
        Get all the TRACKS which are up next. This query does not include
        collections. For example, if an album was queued up, this would return
        all of the tracks queued up, but not the parent "album queue item."
        """
        queue_head = Queue.objects.get_head(stream)
        if not queue_head:
            return Queue.objects.none()
        return self.filter(
            index__gt=queue_head.index,
            stream=stream,
            is_abstract=False,
            deleted_at__isnull=True,
        ).order_by("index")

    def next_up(self, stream):
        """
        This gets all the required data that is needed for managing a user's
        queue. The data is structred as follows:

          - A list of "top level" queue items. Aka, head of the tree hierarchy.
          - All children "track" queue items if the parent is a "collection."
          - For every queue, include the intervals.
        """
        queue_head = Queue.objects.get_head(stream)
        if not queue_head:
            return Queue.objects.none()

        return (
            self.prefetch_related(
                Prefetch(
                    "children",
                    queryset=(
                        Queue.objects.prefetch_active_intervals()
                        .filter(
                            index__gt=queue_head.index,
                            deleted_at__isnull=True,
                        ).order_by("index")
                    ),
                    to_attr="ordered_children",
                )
            )
            .prefetch_active_intervals()
            .filter(
                index__gt=queue_head.index,
                stream=stream,
                parent__isnull=True,
                deleted_at__isnull=True,
            )
            .order_by("index")
        )

    def last_up(self, stream):
        """

        """
        queue_head = Queue.objects.get_head(stream)
        if not queue_head:
            return Queue.objects.none()

        return self.filter(
            index__gte=queue_head.index - 10,
            index__lt=queue_head.index,
            stream=stream,
            is_abstract=False,
            deleted_at__isnull=True,
        ).order_by("index")


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
@pgtrigger.register(
    pgtrigger.Protect(name="protect_inserts", operation=pgtrigger.Insert)
)
class Queue(models.Model):
    """
    A queue is a piece of content (either a track or collection) selected to
    play in a stream. There are two important data structures used here.

      1: LIST        - This is responsible for the order in which tracks are
                       played. The list of queues for a stream are ordered by
                       the index field.
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
    """

    INITIAL_INDEX = 1

    objects = QueueManager.from_queryset(QueueQuerySet)()

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stream = models.ForeignKey(
        "streams.Stream",
        related_name="+",
        on_delete=models.CASCADE,
    )

    index = models.IntegerField(null=True, blank=True)

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

    is_abstract = models.BooleanField()
    parent = models.ForeignKey(
        "streams.Queue",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
    )

    is_head = models.BooleanField(default=False)

    played_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
