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

        # LAST UP
        queue_qs = Queue.objects.last_up(stream)
        last_up_queues = []
        for queue in queue_qs:
            queue_serialized = Queue.objects.serialize(queue)
            last_up_queues.append(queue_serialized)

        # NEXT UP
        queue_qs = Queue.objects.up_next(stream)
        up_next_queues = []
        for queue in queue_qs:
            queue_serialized = Queue.objects.serialize(queue)
            up_next_queues.append(queue_serialized)

        return self.http_response_200(
            {
                "nextUpQueues": up_next_queues,
                "lastUpQueues": last_up_queues,
            }
        )
