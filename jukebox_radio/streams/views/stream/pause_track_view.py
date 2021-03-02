from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core import time as time_util


class StreamPauseTrackView(BaseView, LoginRequiredMixin):

    PARAM_TOTAL_DURATION = "nowPlayingTotalDurationMilliseconds"

    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with self.acquire_playback_control_lock(stream):
            stream = self._pause_track(request, stream)

        return self.http_react_response(
            'stream/pause',
            {
                "pausedAt": time_util.epoch(stream.paused_at),
            }
        )

    def _pause_track(self, request, stream):
        """
        When a user pauses a playing stream.
        """
        if not stream.is_playing:
            raise ValueError("Cannot pause a stream that is not already playing")
        if stream.is_paused:
            raise ValueError("Cannot pause a stream which is already paused")

        pausing_at = time_util.now() + timedelta(milliseconds=100)
        if (stream.started_at - pausing_at) > stream.now_playing_duration:
            raise ValueError(
                "Cannot pause since the track will be over by the time we try to pause"
            )

        stream.paused_at = pausing_at
        stream.save()

        return stream
