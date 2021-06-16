from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_manage_queue_intervals_lock


class QueueIntervalDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Queue = apps.get_model("streams", "Queue")

        queue_uuid = self.param(request, "queueUuid")
        with acquire_manage_queue_intervals_lock(queue_uuid):
            queue = self._delete_queue_interval(request)

        return self.http_react_response(
            "queue/update",
            {
                "queues": [Queue.objects.serialize(queue)],
            },
        )

    def _delete_queue_interval(self, request):
        """
        Delete (archive) a QueueInterval.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        # Query parameters
        queue_interval_uuid = self.param(request, "queueIntervalUuid")

        # Delete the interval
        queue_interval = (
            QueueInterval.objects.select_related("queue")
            .select_related("queue__track")
            .select_related("queue__parent")
            .select_related("lower_bound")
            .select_related("upper_bound")
            .get(uuid=queue_interval_uuid)
        )
        queue_interval.archive()

        queue = queue_interval.queue

        # Update the queue duration
        if queue_interval.purpose == QueueInterval.PURPOSE_MUTED:
            lower_timestamp_ms = getattr(queue_interval.lower_bound, "timestamp_ms", 0)
            upper_timestamp_ms = getattr(
                queue_interval.upper_bound, "timestamp_ms", queue.track.duration_ms
            )
            interval_duration_ms = upper_timestamp_ms - lower_timestamp_ms

            queue.duration_ms += interval_duration_ms
            queue.save()
            if queue.parent:
                # NOTE: This returns the parent queue to the application, which
                #       is expected!
                queue = queue.parent
                queue.duration_ms += interval_duration_ms
                queue.save()

        return queue
