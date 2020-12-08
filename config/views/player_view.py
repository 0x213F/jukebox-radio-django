from urllib.parse import urlencode

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_CHOICES


class PlayerView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        TODO
        """
        Collection = apps.get_model("music", "Collection")
        Stream = apps.get_model("streams", "Stream")
        Queue = apps.get_model("streams", "Queue")

        stream, _ = Stream.objects.get_or_create(user=request.user)

        queue_qs = Queue.objects.in_stream(stream)

        format_choices = [("track", "Track"), ("video", "Video")] + list(
            Collection.FORMAT_CHOICES
        )

        return self.template_response(
            request,
            "pages/player.html",
            {
                "queues": queue_qs,
                "FORMAT_CHOICES": format_choices,
                "PROVIDER_CHOICES": GLOBAL_PROVIDER_CHOICES,
            },
        )
