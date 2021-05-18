from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_manage_queue_intervals_lock


class QueueIntervalStopView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants stop a queue item at a marker.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_uuid = self.param(request, "queueUuid")
        with acquire_manage_queue_intervals_lock(queue_uuid):
            deleted_queue_intervals, queue_interval = self._stop_queue_interval(request)

        # needed for React Redux to update the state on the FE
        parent_queue_uuid = self.param(request, "parentQueueUuid")

        return self.http_react_response(
            "queueInterval/stop",
            {
                "queueInterval/delete": [
                    {
                        "queueInterval": q,
                        "queueUuid": q["queueUuid"],
                        "parentQueueUuid": parent_queue_uuid,
                    } for q in deleted_queue_intervals
                ],
                "queueInterval/create": [
                    {
                        "queueInterval": QueueInterval.objects.serialize(queue_interval),
                        "queueUuid": str(queue_interval.queue_id),
                        "parentQueueUuid": parent_queue_uuid,
                    }
                ],
            },
        )

    def _stop_queue_interval(self, request):
        """
        "Stop" queue by creating a QueueInterval.
        """
        Marker = apps.get_model("streams", "Marker")
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_uuid = self.param(request, "queueUuid")
        marker_uuid = self.param(request, "markerUuid")
        purpose = QueueInterval.PURPOSE_MUTED

        with transaction.atomic():
            marker = Marker.objects.get(uuid=marker_uuid)

            deleted_queue_intervals = []
            queue_interval_qs = (
                QueueInterval
                .objects
                .filter(
                    queue_id=queue_uuid,
                    lower_bound__timestamp_ms__gte=marker.timestamp_ms,
                    deleted_at__isnull=True,
                )
            )

            for queue_interval in queue_interval_qs:
                deleted_queue_intervals.append(
                    QueueInterval.objects.serialize(queue_interval)
                )
                queue_interval.archive()

            queue_interval = QueueInterval.objects.create_queue_interval(
                user=request.user,
                queue_id=queue_uuid,
                lower_bound_id=marker_uuid,
                upper_bound_id=None,
                purpose=purpose,
            )

        return deleted_queue_intervals, queue_interval
