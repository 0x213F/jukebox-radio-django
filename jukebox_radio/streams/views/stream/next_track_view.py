from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamNextTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")
        Queue = apps.get_model("streams", "Queue")

        stream = Stream.objects.select_related("now_playing").get(user=request.user)
        with acquire_playback_control_lock(stream):
            stream = self._next_track(request, stream)

        return self.http_react_response(
            "queue/update",
            {
                "queues": [Queue.objects.serialize(stream.now_playing)],
            },
        )

    def _next_track(self, request, stream):
        Queue = apps.get_model("streams", "Queue")

        total_duration_ms = stream.now_playing.duration_ms
        if total_duration_ms:
            total_duration = timedelta(milliseconds=int(total_duration_ms))
        is_planned = self.param(request, "isPlanned")

        next_head = Queue.objects.get_next(stream)

        if not next_head:

            if not stream.now_playing.is_playing and not stream.now_playing.is_paused:
                raise ValueError("Stream needs to be playing or paused")

            stream.now_playing.status_at = time_util.now()
            stream.now_playing.status = Queue.STATUS_ENDED_AUTO
            stream.now_playing.save()
            return stream

        if is_planned:
            playing_at = stream.now_playing.started_at + total_duration
        else:
            playing_at = time_util.now() + timedelta(milliseconds=100)

        with transaction.atomic():

            next_head.started_at = playing_at
            next_head.status = Queue.STATUS_PLAYED
            next_head.status_at = time_util.now()
            next_head.save()

            prev_head = stream.now_playing
            prev_head.status = Queue.STATUS_ENDED_AUTO
            prev_head.status_at = time_util.now()
            prev_head.save()

            stream.now_playing = next_head
            stream.save()

        return stream
