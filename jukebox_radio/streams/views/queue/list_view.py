from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Get a list of all active queues in a stream. A queue becomes inactive
        if it is either played or deleted (aka archived).
        """
        Queue = apps.get_model('streams', 'Queue')
        Stream = apps.get_model('streams', 'Stream')

        stream = Stream.objects.get(user=request.user)
        queue_qs = Queue.objects.in_stream(stream)

        queues = []
        for queue in queue_qs:
            queues.append(
                {
                    "uuid": queue.uuid,
                    "trackName": queue.track.name,
                    "collectionName": queue.collection.name,
                    "trackDurationMs": queue.track.duration_ms,
                    "parentQueuePtrUuid": queue.parent_queue_ptr_id,
                    "isAbstract": queue.is_abstract,
                }
            )

        return self.http_response_200(queues)
