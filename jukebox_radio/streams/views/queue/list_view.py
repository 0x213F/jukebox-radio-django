from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class QueueListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        TODO
        """
        Queue = apps.get_model('streams', 'Queue')
        Stream = apps.get_model('streams', 'Stream')

        stream = Stream.objects.get(user=request.user)
        queue_qs = Queue.objects.filter(in_stream=stream)
        queues = []
        for queue in queue_qs:
            queues.append(
                {
                    "uuid": queue.uuid,
                    "trackName": queue.track.name,
                    "trackDurationMs": queue.track.duration_ms,
                    "collectionName": queue.collection.name,
                }
            )

        return self.http_response_200(queues)
