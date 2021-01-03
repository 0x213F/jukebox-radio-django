from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView


class StreamPlayTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user plays a paused stream.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if stream.is_playing:
            raise ValueError("Cannot play a stream which is already playing")
        if not stream.is_paused:
            raise ValueError("Cannot play a stream which is not paused")

        playing_at = timezone.now()
        paused_duration = playing_at - stream.paused_at

        stream.played_at += paused_duration
        stream.paused_at = None
        stream.save()

        return self.http_response_200({
            "playedAt": int(stream.played_at.timestamp()),
        })
