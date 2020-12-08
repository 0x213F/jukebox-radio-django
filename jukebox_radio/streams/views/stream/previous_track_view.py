from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class StreamPreviousTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        TODO
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.now_playing_id:
            raise ValueError('Nothing is playing!')

        playing_at = timezone.now() + timedelta(milliseconds=125)

        stream.played_at = playing_at
        stream.paused_at = None
        stream.save()

        return self.http_response_200({})
