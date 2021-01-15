from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueIntervalDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Delete (archive) a QueueInterval.
        """
        QueueInterval = apps.get_model("streams", "QueueInterval")

        queue_interval_uuid = request.POST.get("queueIntervalUuid")

        queue_interval = QueueInterval.objects.get(uuid=queue_interval_uuid)
        queue_interval.archive()

        return self.http_response_200()
