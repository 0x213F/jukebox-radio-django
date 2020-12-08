from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class QueueDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Remove from queue.
        """
        Queue = apps.get_model("streams", "Queue")

        queue_uuid = request.POST.get("queueUuid")

        queue = Queue.objects.select_related("prev_queue_ptr", "next_queue_ptr").get(
            uuid=queue_uuid, user=request.user
        )

        now = timezone.now()
        with transaction.atomic():

            # delete queue
            queue.deleted_at = now
            queue.save()

            # fix prev pointer
            queue.prev_queue_ptr.next_queue_ptr = queue.next_queue_ptr
            queue.prev_queue_ptr.save()

            # fix next pointer
            queue.next_queue_ptr.prev_queue_ptr = queue.prev_queue_ptr
            queue.next_queue_ptr.save()

            if queue.is_abstract:
                child_queue_qs = Queue.objects.filter(parent_queue_ptr=queue)
                child_queue_qs.update(deleted_at=now)

        return self.http_response_200({})
