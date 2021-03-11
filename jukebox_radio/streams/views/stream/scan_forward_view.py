from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamScanForwardView(BaseView, LoginRequiredMixin):

    PARAM_TOTAL_DURATION = "nowPlayingTotalDurationMilliseconds"

    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with acquire_playback_control_lock(stream):
            stream = self._scan_forward(request, stream)

        return self.http_response_200({})

    def _scan_forward(self, request, stream):
        """
        Scan the stream forwards 10 seconds e.g. double tapping left or right
        in a video streaming app.
        """
        total_duration_ms = self.param(request, self.PARAM_TOTAL_DURATION)
        total_duration = timedelta(milliseconds=int(total_duration_ms))

        if not stream.is_playing:
            raise Exception("Stream has to be playing")

        total_duration_ms = self.param(request, self.PARAM_TOTAL_DURATION)
        total_duration = timedelta(milliseconds=int(total_duration_ms))
        end_buffer = timedelta(seconds=15)
        if not stream.controls_enabled(end_buffer, total_duration):
            raise Exception("Cannot scan backwards at the very end of the song")

        playing_at = stream.started_at - timedelta(seconds=10)
        stream.started_at = playing_at
        stream.save()

        return self.http_response_200({})
