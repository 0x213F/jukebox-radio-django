from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class StreamPauseTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        TODO
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing:
            raise ValueError('Cannot pause a stream that is not already playing')
        if stream.is_paused:
            raise ValueError('Cannot pause a stream which is already paused')

        pausing_at = timezone.now() + timedelta(milliseconds=125)

        stream.paused_at = pausing_at
        stream.save()

        return self.http_response_200({})
