from datetime import timedelta

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class StreamScanBackwardView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Scan backward 10 seconds
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing:
            raise ValueError('Stream has to be playing')

        playing_at = stream.played_at + timedelta(seconds=10)
        lower_bound = timezone.now() + timedelta(milliseconds=125)
        if playing_at > lower_bound:
            playing_at = lower_bound

        stream.played_at = playing_at
        stream.save()

        return self.http_response_200({})
