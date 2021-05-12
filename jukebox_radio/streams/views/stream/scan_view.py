from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamScanView(BaseView, LoginRequiredMixin):

    PARAM_TOTAL_DURATION = "nowPlayingTotalDurationMilliseconds"
    PARAM_STARTED_AT = "startedAt"

    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with acquire_playback_control_lock(stream):
            stream = self._scan(request, stream)

        return self.http_response_200({})

    def _scan(self, request, stream):
        """
        Scans the stream to a specific part of the currently playing track.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing:
            raise Exception("Stream has to be playing")

        total_duration_ms = self.param(request, self.PARAM_TOTAL_DURATION)
        total_duration = timedelta(milliseconds=int(total_duration_ms))
        started_at_raw = self.param(request, self.PARAM_STARTED_AT)
        started_at = time_util.int_to_dt(int(started_at_raw))
        now = time_util.now()

        valid_started_at = (
            now > started_at and
            now < started_at + total_duration - timedelta(seconds=5)
        )

        if not valid_started_at:
            raise Exception("Invalid scan")

        stream.started_at = started_at
        stream.save()

        return stream
