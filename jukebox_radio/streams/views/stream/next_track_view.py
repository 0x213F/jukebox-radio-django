from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamNextTrackView(BaseView, LoginRequiredMixin):

    PARAM_TOTAL_DURATION = "nowPlayingTotalDurationMilliseconds"

    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with acquire_playback_control_lock(stream):
            stream = self._next_track(request, stream)

        return self.http_react_response(
            "stream/nextTrack",
            {
                "startedAt": time_util.epoch(stream.started_at),
            },
        )

    def _next_track(self, request, stream):
        Queue = apps.get_model("streams", "Queue")

        total_duration_ms = self.param(request, self.PARAM_TOTAL_DURATION)
        if total_duration_ms:
            total_duration = timedelta(milliseconds=int(total_duration_ms))
        is_planned = self.param(request, "isPlanned")

        last_head = Queue.objects.get_head(stream)
        next_head = Queue.objects.get_next(stream)

        if not next_head:

            if not stream.is_playing and not stream.is_paused:
                raise ValueError("Stream needs to be playing or paused")

            stream.started_at = time_util.now() - total_duration
            stream.paused_at = None
            stream.save()
            return stream

        if is_planned:
            playing_at = stream.started_at + total_duration
        else:
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
