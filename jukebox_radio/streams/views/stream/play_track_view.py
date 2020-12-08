from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class StreamPlayTrackView(BaseView, LoginRequiredMixin):
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
        except KeyError:
            raise ValueError("Queue is empty!")

        playing_at = timezone.now() + timedelta(milliseconds=125)

        with transaction.atomic():
            stream.now_playing = first_queue.track
            stream.played_at = playing_at
            stream.is_playing = True
            stream.save()

            first_queue.played_at = playing_at
            first_queue.save()

        return self.http_response_200({})
