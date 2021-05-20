from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamPauseTrackView(BaseView, LoginRequiredMixin):

    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.select_related('now_playing').get(user=request.user)
        with acquire_playback_control_lock(stream):
            stream = self._pause_track(request, stream)

        return self.http_react_response(
            "stream/pause",
            {
                "statusAt": time_util.epoch(stream.now_playing.status_at),
                "status": stream.now_playing.status,
            },
        )

    def _pause_track(self, request, stream):
        """
        When a user pauses a playing stream.
        """
        Queue = apps.get_model("streams", "Queue")
        if not stream.now_playing.is_playing:
            raise ValueError("Cannot pause a stream that is not already playing")
        if stream.now_playing.is_paused:
            raise ValueError("Cannot pause a stream which is already paused")

        pausing_at = time_util.now() + timedelta(milliseconds=100)
        if not stream.now_playing.controls_enabled:
            raise ValueError(
                "Cannot pause since the track will be over by the time we try to pause"
            )

        stream.now_playing.status = Queue.STATUS_PAUSED
        stream.now_playing.status_at = pausing_at
        stream.now_playing.save()

        return stream
