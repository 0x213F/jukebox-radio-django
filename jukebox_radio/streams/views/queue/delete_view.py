from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class QueueDeleteView(BaseView, LoginRequiredMixin):
    def delete(self, request, **kwargs):
        """
        Delete a Queue.
        """
        Queue = apps.get_model("streams", "Queue")

        queue_uuid = request.DELETE.get("queueUuid")

        queue = Queue.objects.get(uuid=queue_uuid, user=request.user)
        queue.delete()

        return self.http_response_200(
            {
                "uuid": queue_uuid,
            }
        )
