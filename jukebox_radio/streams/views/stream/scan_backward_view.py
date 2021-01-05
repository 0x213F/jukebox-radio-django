from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView


class StreamScanBackwardView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Scan the stream backwards 10 seconds e.g. double tapping left or right
        in a video streaming app.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing:
            raise ValueError("Stream has to be playing")

        playing_at = stream.started_at + timedelta(seconds=10)
        lower_bound = timezone.now() + timedelta(milliseconds=125)
        if playing_at > lower_bound:
            playing_at = lower_bound

        stream.started_at = playing_at
        stream.save()

        return self.http_response_200({})
