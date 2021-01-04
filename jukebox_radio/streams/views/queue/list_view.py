from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Get a list of all active queues in a stream. A queue becomes inactive
        if it is either played or deleted (aka archived).
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        # UP NEXT
        queue_qs = Queue.objects.up_next(stream)

        up_next_queues = []
        for queue in queue_qs:

            if queue.collection and not queue.ordered_children:
                continue

            children = []
            for child in queue.ordered_children:
                track_name = child.track and child.track.name
                track_duration_ms = child.track and child.track.duration_ms
                children.append(
                    {
                        "uuid": child.uuid,
                        "index": child.index,
                        "trackName": track_name,
                        "trackDurationMs": track_duration_ms,
                        "parentUuid": child.parent_id,
                        "isAbstract": child.is_abstract,
                        "children": [],
                        "isDeleted": bool(child.deleted_at),
                        "depth": 1,
                    }
                )

            track_name = queue.track and queue.track.name
            collection_name = queue.collection and queue.collection.name
            track_duration_ms = queue.track and queue.track.duration_ms
            up_next_queues.append(
                {
                    "uuid": queue.uuid,
                    "index": queue.index,
                    "trackName": track_name,
                    "collectionName": collection_name,
                    "trackDurationMs": track_duration_ms,
                    "parentUuid": queue.parent_id,
                    "isAbstract": queue.is_abstract,
                    "children": children,
                    "isDeleted": False,
                    "depth": 0,
                }
            )

        # LAST UP
        queue_qs = Queue.objects.last_up(stream)

        last_up_queues = []
        for queue in queue_qs:
            track_name = queue.track and queue.track.name
            collection_name = queue.collection and queue.collection.name
            track_duration_ms = queue.track and queue.track.duration_ms
            last_up_queues.append(
                {
                    "uuid": queue.uuid,
                    "index": queue.index,
                    "trackName": track_name,
                    "collectionName": collection_name,
                    "trackDurationMs": track_duration_ms,
                    "parentUuid": queue.parent_id,
                    "isAbstract": queue.is_abstract,
                    "isDeleted": False,
                    "depth": 0,
                }
            )

        return self.http_response_200(
            {
                "nextUpQueues": up_next_queues,
                "lastUpQueues": last_up_queues,
            }
        )
