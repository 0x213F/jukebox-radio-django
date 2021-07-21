from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_playback_control_lock


class StreamPlayTrackView(BaseView, LoginRequiredMixin):

    PARAM_TIMESTAMP_MS = "startedAt"

    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")
        Queue = apps.get_model("streams", "Queue")

        stream = Stream.objects.select_related("now_playing").get(user=request.user)
        with acquire_playback_control_lock(stream):
            stream = self._play_track(request, stream)

        return self.http_react_response(
            "queue/update",
            {
                "queues": [Queue.objects.serialize(stream.now_playing)],
            },
        )

    def _play_track(self, request, stream):
        """
        When a user plays a paused stream.
        """
        Queue = apps.get_model("streams", "Queue")
        if stream.now_playing.is_playing:
            raise ValueError("Cannot play a stream which is already playing")
        if not stream.now_playing.is_paused:
            raise ValueError("Cannot play a stream which is not paused")

        # NOTE: We have to be able to get ourselves out of a pickle. So here,
        #       we do not restrict the play action by checking to see if the
        #       stream has `controls_enabled`. So long as the stream is paused,
        #       we allow the play action.

        # NOTE: This is a copy paste of "scan" logic found in "scan_view."
        total_duration_ms = stream.now_playing.duration_ms
        total_duration = timedelta(milliseconds=int(total_duration_ms))
        timestamp_ms = self.param(request, self.PARAM_TIMESTAMP_MS)

        now = time_util.now()
        started_at = now - timedelta(milliseconds=int(timestamp_ms))

        # Needs validation when scanning
        valid_started_at = (
            now >= started_at
            and now < started_at + total_duration - timedelta(seconds=5)
        )
        if not valid_started_at:
            raise Exception("Invalid scan")

        stream.now_playing.started_at = started_at
        stream.now_playing.status_at = time_util.now()
        stream.now_playing.status = Queue.STATUS_PLAYED
        stream.now_playing.save()

        return stream
