from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class QueueListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List Queue objects that the user has created for a given stream.
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=user)

        queue_qs = Queue.objects.filter(stream=stream, played_at__isnull=True)

        queues = []
        for queue in queue_qs:
            queue.append(
                {
                    "id": queue.id,
                    "trackId": queue.track_id,
                    "collectionId": queue.collection_id,
                    "streamId": queue.stream_id,
                    "prevQueuePtr": queue.prev_queue_ptr_id,
                    "nextQueuePtr": queue.next_queue_ptr_id,
                    "isAbstract": queue.is_abstract,
                }
            )

        return self.http_response_200(queues)
