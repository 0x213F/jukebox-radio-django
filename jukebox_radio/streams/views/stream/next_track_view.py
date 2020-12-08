from datetime import timedelta

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class StreamNextTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        In the user's stream, play the head of the queue.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        try:
            first_queue = Queue.objects.in_stream(stream)[0]
        except IndexError:
            raise ValueError("Queue is empty!")

        with transaction.atomic():
            playing_at = timezone.now() + timedelta(milliseconds=125)

            stream.now_playing = first_queue.track
            stream.played_at = playing_at
            stream.paused_at = None
            stream.save()

            first_queue.played_at = playing_at
            first_queue.save()

        return self.http_response_200({})
