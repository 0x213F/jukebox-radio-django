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
        When a user deletes something from the queue. In this case, what is
        actually happening is queue archival. The queue is deleted in the
        application layer but persists in the database.
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

            # fix prev pointers
            next_queue_qs = Queue.objects.filter(next_queue_ptr=queue)
            next_queue_qs.update(next_queue_ptr=queue.next_queue_ptr)

            # fix next pointers
            prev_queue_qs = Queue.objects.filter(prev_queue_ptr=queue)
            prev_queue_qs.update(prev_queue_ptr=queue.prev_queue_ptr)

            # delete child queues
            child_queue_qs = Queue.objects.filter(parent_queue_ptr=queue)
            child_queue_qs.update(deleted_at=now)

        return self.http_response_200({})
