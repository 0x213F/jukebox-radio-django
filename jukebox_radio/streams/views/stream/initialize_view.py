from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class StreamInitializeView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user initializes a stream (right after login).
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream, created = Stream.objects.get_or_create(user=request.user)

        if not created:
            return self.http_response_200()

        Queue.objects.create_initial_queue(stream)

        return self.http_response_200()
