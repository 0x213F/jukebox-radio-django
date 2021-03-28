from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class StreamInitializeView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user initializes a stream (called right after login).
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream, created = Stream.objects.get_or_create(user=request.user)

        if Queue.objects.filter(stream=stream, deleted_at__isnull=True).exists():
            return self.http_response_200()

        queue = Queue.objects.create_blank_queue(stream)
        stream.now_playing = queue
        stream.save()

        return self.http_response_200()
