from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView


class StreamPreviousTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "last played track" right now.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        last_head = Queue.objects.get_head(stream)
        next_head = Queue.objects.get_prev(stream)

        if not next_head:
            raise ValueError("Nothing to play next!")

        playing_at = timezone.now()
        with transaction.atomic():

            stream.now_playing = next_head.track
            stream.played_at = playing_at
            stream.paused_at = None
            stream.save()

            next_head.played_at = playing_at
            next_head.is_head = True
            next_head.save()

            last_head.is_head = False
            last_head.save()

        return self.http_response_200({})
