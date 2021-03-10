from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamPlayTrackView(BaseView, LoginRequiredMixin):

    PARAM_TOTAL_DURATION = "nowPlayingTotalDurationMilliseconds"

    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with self.acquire_playback_control_lock(stream):
            stream = self._play_track(request, stream)

        return self.http_react_response(
            "stream/play",
            {
                "startedAt": time_util.epoch(stream.started_at),
            },
        )

    def _play_track(self, request, stream):
        """
        When a user plays a paused stream.
        """
        if stream.is_playing:
            raise ValueError("Cannot play a stream which is already playing")
        if not stream.is_paused:
            raise ValueError("Cannot play a stream which is not paused")

        # NOTE: We have to be able to get ourselves out of a pickle. So here,
        #       we do not restrict the play action by checking to see if the
        #       stream has `controls_enabled`. So long as the stream is paused,
        #       we allow the play action.

        playing_at = time_util.now() + timedelta(milliseconds=100)
        paused_duration = playing_at - stream.paused_at

        stream.started_at += paused_duration
        stream.paused_at = None
        stream.save()

        return stream
