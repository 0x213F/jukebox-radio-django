from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List relevant queues in a stream.

            - last_up_queues: the 10 most recent queues
            - next_up_queues: all upcoming queues
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        # last up
        queue_qs = Queue.objects.last_up(stream)
        last_up_queues = []
        for queue in queue_qs:
            queue_serialized = Queue.objects.serialize(queue)
            last_up_queues.append(queue_serialized)

        # next up
        queue_qs = Queue.objects.next_up(stream)
        next_up_queues = []
        for queue in queue_qs:
            queue_serialized = Queue.objects.serialize(queue)
            next_up_queues.append(queue_serialized)

        return self.http_response_200(
            {
                "lastUpQueues": last_up_queues,
                "nextUpQueues": next_up_queues,
            }
        )
