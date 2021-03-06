from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_modify_queue_lock


class QueueDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with acquire_modify_queue_lock(stream):
            stream = self._delete_queue(request, stream)

        return self.http_response_200()

    def _delete_queue(self, request, stream):
        """
        When a user deletes (archives) something from the queue.
        """
        Queue = apps.get_model("streams", "Queue")

        queue_uuid = self.param(request, "queueUuid")
        queue = Queue.objects.get(uuid=queue_uuid, stream=stream, user=request.user)

        now = time_util.now()
        with transaction.atomic():

            # delete queue
            queue.deleted_at = now
            queue.save()

            # fix offset for up next indexes
            children_queue_count = queue.children.count()
            offset = max(1, children_queue_count)
            relative_next_up = Queue.objects.filter(
                stream=stream, index__gt=queue.index, deleted_at__isnull=True
            )
            relative_next_up.update(index=F("index") - offset)

            # also delete children
            queue.children.all().update(deleted_at=now)
