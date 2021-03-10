from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamPrevTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "last up queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with self.acquire_playback_control_lock(stream):
            stream = self._prev_track(request, stream)

        return self.http_react_response(
            "stream/prevTrack",
            {
                "startedAt": time_util.epoch(stream.started_at),
            },
        )

    def _prev_track(self, request, stream):
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")

        if not stream.now_playing.track_id:
            raise ValueError("Nothing to play next!")

        if not stream.is_playing and not stream.is_paused and stream.now_playing:
            playing_at = time_util.now()
            stream.started_at = playing_at
            stream.paused_at = None
            stream.save()
            return stream

        last_head = Queue.objects.get_head(stream)
        next_head = Queue.objects.get_prev(stream)

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

        return stream
