from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamPrevTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "last up queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.select_related('now_playing').get(user=request.user)
        with acquire_playback_control_lock(stream):
            stream = self._prev_track(request, stream)

        return self.http_react_response(
            "stream/prevTrack",
            {
                "startedAt": time_util.epoch(stream.now_playing.started_at),
                "statusAt": time_util.epoch(stream.now_playing.status_at),
                "status": stream.now_playing.status,
            },
        )

    def _prev_track(self, request, stream):
        Queue = apps.get_model("streams", "Queue")

        if not stream.now_playing.track_id:
            raise ValueError("Nothing to play next!")

        if stream.now_playing and not stream.now_playing.is_playing and not stream.now_playing.is_paused:
            playing_at = time_util.now()
            stream.now_playing.started_at = playing_at
            stream.now_playing.status = Queue.STATUS_PLAYED
            stream.now_playing.status_at = time_util.now()
            stream.now_playing.save()
            return stream

        next_head = Queue.objects.get_prev(stream)

        playing_at = time_util.now() + timedelta(milliseconds=100)
        with transaction.atomic():

            next_head.started_at = playing_at
            next_head.status = Queue.STATUS_PLAYED
            next_head.status_at = time_util.now()
            next_head.save()

            prev_head = stream.now_playing
            prev_head.status_at = time_util.now()
            prev_head.status = Queue.STATUS_QUEUED_PREVIOUS
            prev_head.save()

            stream.now_playing = next_head
            stream.save()

        return stream
