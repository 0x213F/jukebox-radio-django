import uuid
from datetime import timedelta

import pgtrigger
from django.apps import apps
from django.db import models, transaction
from django.db.models import F, Prefetch

from jukebox_radio.core import time as time_util


class QueueManager(models.Manager):
    def serialize(self, queue):
        Collection = apps.get_model("music", "Collection")
        Track = apps.get_model("music", "Track")
        Marker = apps.get_model("streams", "Marker")
        QueueInterval = apps.get_model("streams", "QueueInterval")

        if not queue:
            return None

        track = Track.objects.serialize(queue.track) if queue.track_id else None
        collection = (
            Collection.objects.serialize(queue.collection)
            if queue.collection_id
            else None
        )

        obj = {
            "uuid": queue.uuid,
            "index": queue.index,
            "track": track,
            "collection": collection,
            "parentUuid": queue.parent_id,
            "isAbstract": queue.is_abstract,
            "isArchived": bool(queue.deleted_at),
            "durationMilliseconds": queue.duration_ms,
            "startedAt": time_util.epoch(queue.started_at),
            "status": queue.status,
            "statusAt": time_util.epoch(queue.status_at),
        }

        try:
            queue_children = queue.ordered_children
        except AttributeError:
            # NOTE: We should fetch children here, but as of now, no case
            #       justifies writing this code.
            queue_children = []
        children = []
        for child in queue_children:
            children.append(self.serialize(child))
        obj["children"] = children

        try:
            active_intervals = queue.active_intervals
        except AttributeError:
            active_intervals = (
                QueueInterval.objects
                .filter(queue_id=queue.uuid, deleted_at__isnull=True)
                .order_by("upper_bound__timestamp_ms")
            )
        intervals = []
        for interval in active_intervals:
            intervals.append(QueueInterval.objects.serialize(interval))
        obj["intervals"] = intervals

        try:
            active_markers = queue.active_markers
        except AttributeError:
            active_markers = (
                Marker.objects
                .filter(track_id=queue.track_id, deleted_at__isnull=True)
                .order_by("timestamp_ms")
            )
        markers = []
        for marker in active_markers:
            markers.append(Marker.objects.serialize(marker))
        obj["markers"] = markers

        return obj

    @pgtrigger.ignore("streams.Queue:protect_inserts")
    def create_blank_queue(self, stream):
        """
        Custom create method.
        TODO: this should probably only be done when the blank queue is the
        new head. the code should enforce that.
        """
        Queue = apps.get_model("streams", "Queue")

        head = Queue.objects.get_head(stream)
        if head:
            index = head.index + 1
        else:
            index = Queue.INITIAL_INDEX

        return Queue.objects.create(
            stream=stream,
            user=stream.user,
            index=index,
            is_abstract=False,
            duration_ms=0,
            status=Queue.STATUS_PLAYED,
            status_at=time_util.now(),
        )

    @pgtrigger.ignore("streams.Queue:protect_inserts")
    def create_queue(
        self, stream=None, track=None, collection=None, user=None, **kwargs
    ):
        """
        Custom create method
        """
        Queue = apps.get_model("streams", "Queue")

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
                    status=Queue.STATUS_QUEUED_INIT,
                    status_at=time_util.now(),
                )
                if collection
                else None
            )
            if parent_queue:
                queues.append(parent_queue)

            total_duration_ms = 0
            for _track in _tracks:
                t = _track or track
                queue = Queue(
                    stream=stream,
                    index=index,
                    user=user,
                    track=(_track or track),
                    collection=collection,
                    is_abstract=False,
                    parent=parent_queue,
                    duration_ms=t.duration_ms,
                    status=Queue.STATUS_QUEUED_INIT,
                    status_at=time_util.now(),
                )
                queues.append(queue)
                index += 1
                total_duration_ms += t.duration_ms
            if parent_queue:
                parent_queue.duration_ms = total_duration_ms

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
                    QueueInterval.objects.select_related("lower_bound", "upper_bound")
                    .filter(deleted_at__isnull=True)
                    .order_by("upper_bound__timestamp_ms")
                ),
                to_attr="active_intervals",
            )
        )

    def prefetch_active_markers(self):
        """
        Simple prefetch of queue intervals. This is needed because the deleted
        (archived) intervals should not be included in the query.

        We also join the bounds using select related since they are needed in
        context of the queue intervals.
        """
        Marker = apps.get_model("streams", "Marker")

        return self.prefetch_related(
            Prefetch(
                "track__markers",
                queryset=Marker.objects.filter(deleted_at__isnull=True).order_by("timestamp_ms"),
                to_attr="active_markers",
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
        """
        try:
            return Queue.objects.get(
                uuid=stream.now_playing_id,
                stream=stream,
                deleted_at__isnull=True,
            )
        except Queue.DoesNotExist:
            return None

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
            self
            .select_related("track", "collection")
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=(
                        Queue.objects
                        .select_related("track", "collection")
                        .prefetch_active_intervals()
                        .prefetch_active_markers()
                        .filter(
                            index__gt=queue_head.index,
                            deleted_at__isnull=True,
                        )
                        .order_by("index")
                    ),
                    to_attr="ordered_children",
                )
            )
            .prefetch_active_intervals()
            .prefetch_active_markers()
            .filter(
                index__gt=queue_head.index,
                stream=stream,
                parent__isnull=True,
                deleted_at__isnull=True,
            )
            .order_by("index")
        )

    def last_up(self, stream):
        """"""
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

    CONTROL_BUFFER_MS = 6000

    INITIAL_INDEX = 1

    STATUS_QUEUED_INIT = "queued_init"
    STATUS_PLAYED = "played"
    STATUS_PAUSED = "paused"
    STATUS_ENDED_AUTO = "ended_auto"
    STATUS_ENDED_SKIPPED = "ended_skip"
    STATUS_QUEUED_PREVIOUS = "queued_previous"

    STATUS_CHOICES = [
        (STATUS_QUEUED_INIT, "Queued (init)"),
        (STATUS_PLAYED, "Played"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_ENDED_AUTO, "Ended (auto)"),
        (STATUS_ENDED_SKIPPED, "Ended (skipped)"),
        (STATUS_QUEUED_PREVIOUS, "Queued (previous)"),
    ]

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

    duration_ms = models.PositiveIntegerField()

    started_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    status_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_playing(self):
        return self.status == self.STATUS_PLAYED

    @property
    def is_paused(self):
        return self.status == self.STATUS_PAUSED

    def controls_enabled(self, end_buffer, total_duration):
        """
        A stream's playback controls are disabled towards the end of the now
        playing track. This determines if the stream is able to have the
        controls enabled or not.
        """
        if not self.track_id:
            raise Exception("Can only control a queue if it has a track.")

        if self.status == self.STATUS_PAUSED:
            return True

        if self.status != self.STATUS_PLAYED:
            return False

        expected_end_at = self.started_at + timedelta(milliseconds=self.track.duration_ms)
        controls_disabled_at = time_util.now() + timedelta(milliseconds=self.CONTROL_BUFFER_MS)

        return controls_disabled_at > expected_end_at
