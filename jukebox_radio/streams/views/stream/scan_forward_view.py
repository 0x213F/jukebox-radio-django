from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView


class StreamScanForwardView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Scan the stream forwards 10 seconds e.g. double tapping left or right
        in a video streaming app.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing:
            raise ValueError("Stream has to be playing")

        playing_at = stream.played_at - timedelta(seconds=10)
        now = timezone.now()
        track_ends_at = playing_at + timedelta(milliseconds=stream.now_playing.duration_ms)
        if track_ends_at <= now:
            raise ValueError("Cannot scan past the end of the song")

        stream.played_at = playing_at
        stream.save()

        return self.http_response_200({})
