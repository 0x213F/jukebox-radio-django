from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueIntervalDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_uuid = self.param(request, "queueUuid")
        with self.acquire_manage_queue_intervals_lock(queue_uuid):
            queue_interval = self._delete_queue_interval(request)

        # needed for React Redux to update the state on the FE
        parent_queue_uuid = self.param(request, "parentQueueUuid")

        return self.http_react_response(
            "queueInterval/delete",
            {
                "queueInterval": QueueInterval.objects.serialize(queue_interval),
                "queueUuid": queue_uuid,
                "parentQueueUuid": parent_queue_uuid,
            },
        )

    def _delete_queue_interval(self, request):
        """
        Delete (archive) a QueueInterval.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_interval_uuid = self.param(request, "queueIntervalUuid")
        queue_interval = QueueInterval.objects.get(uuid=queue_interval_uuid)
        queue_interval.archive()

        return queue_interval
