from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class StreamGetView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        When a user plays a paused stream.
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        now_playing_serialized = Queue.objects.serialize(stream.now_playing)

        return self.http_response_200(
            {
                "uuid": stream.uuid,
                "nowPlaying": now_playing_serialized,
                "isPlaying": stream.is_playing,
                "isPaused": stream.is_paused,
                "startedAt": stream.started_at and int(stream.started_at.timestamp() * 1000),
                "pausedAt": stream.paused_at and int(stream.paused_at.timestamp() * 1000),
            }
        )
