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

        return self.http_react_response(
            "stream/set",
            {
                "stream": Stream.objects.serialize(stream),
            },
        )
