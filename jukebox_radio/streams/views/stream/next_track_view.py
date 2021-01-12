from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core import time as time_util


class StreamNextTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        last_head = Queue.objects.get_head(stream)
        next_head = Queue.objects.get_next(stream)

        if not next_head:

            if not stream.is_playing and not stream.is_paused:
                raise ValueError("Stream needs to be playing or paused")

            stream.started_at = time_util.now() - stream.now_playing_duration
            stream.paused_at = None
            stream.save()
            return self.http_response_200(
                {
                    "startedAt": int(stream.started_at.timestamp()),
                }
            )

        playing_at = time_util.now() + timedelta(milliseconds=100)
        with transaction.atomic():

            stream.now_playing = next_head
            stream.started_at = playing_at
            stream.paused_at = None
            stream.save()

            next_head.played_at = playing_at
            next_head.is_head = True
            next_head.save()

            last_head.is_head = False
            last_head.save()

        return self.http_response_200(
            {
                "startedAt": int(stream.started_at.timestamp()),
            }
        )
