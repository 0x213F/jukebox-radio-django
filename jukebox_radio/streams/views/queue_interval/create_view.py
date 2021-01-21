from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueIntervalCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
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

        return self.http_react_response(
            'queueInterval/create',
            {
                "queueInterval": QueueInterval.objects.serialize(queue_interval),
                "queueUuid": queue_uuid,
                "parentQueueUuid": parent_queue_uuid,
            }
        )
