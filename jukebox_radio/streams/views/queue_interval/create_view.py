from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueIntervalCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_uuid = self.param(request, "queueUuid")
        with self.acquire_manage_queue_intervals_lock(queue_uuid):
            queue_interval = self._create_queue_interval(request)

        # needed for React Redux to update the state on the FE
        parent_queue_uuid = self.param(request, "parentQueueUuid")

        return self.http_react_response(
            'queueInterval/create',
            {
                "queueInterval": QueueInterval.objects.serialize(queue_interval),
                "queueUuid": queue_uuid,
                "parentQueueUuid": parent_queue_uuid,
            }
        )

    def _create_queue_interval(self, request):
        """
        Create a QueueInterval.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_uuid = self.param(request, "queueUuid")
        lower_bound_marker_uuid = self.param(request, "lowerBoundMarkerUuid")
        upper_bound_marker_uuid = self.param(request, "upperBoundMarkerUuid")
        queue_interval = QueueInterval.objects.create_queue_interval(
            user=request.user,
            queue_id=queue_uuid,
            lower_bound_id=lower_bound_marker_uuid,
            upper_bound_id=upper_bound_marker_uuid,
            is_muted=True,
        )

        # needed for React Redux to update the state on the FE
        parent_queue_uuid = self.param(request, "parentQueueUuid")

        return queue_interval
