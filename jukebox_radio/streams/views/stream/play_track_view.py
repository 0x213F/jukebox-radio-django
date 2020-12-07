from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class StreamPlayTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        TODO
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.now_playing_id:
            try:
                first_queue = Queue.objects.get(
                    stream=stream,
                    prev_queue_ptr=None,
                    played_at__isnull=True,
                    deleted_at__isnull=True,
                )
            except Queue.DoesNotExist:
                raise ValueError("Queue is empty!")

            playing_at = timezone.now() + timedelta(seconds=1)

            # TODO ... wrap with transaction
            stream.now_playing = first_queue.track
            stream.played_at = playing_at
            stream.is_playing = True
            stream.save()

            queue.is_head = False
            queue.save()

            next_queue = queue.next_queue_ptr
            if next_queue:
                next_queue.is_head = True

            return self.http_response_200({})

        else:
            return self.http_response_200({})
