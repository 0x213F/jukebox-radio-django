from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueIntervalCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a QueueInterval.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_uuid = request.POST.get("queueUuid")

        lower_bound_marker_uuid = request.POST.get("lowerBoundMarkerUuid")
        upper_bound_marker_uuid = request.POST.get("upperBoundMarkerUuid")

        is_muted = request.POST.get("isMuted") == "true"

        queue_interval = QueueInterval.objects.create_queue_interval(
            user=request.user,
            queue_id=queue_uuid,
            lower_bound_id=lower_bound_marker_uuid,
            upper_bound_id=upper_bound_marker_uuid,
            is_muted=is_muted,
        )

        return self.http_response_200(
            QueueInterval.objects.serialize(queue_interval)
        )
