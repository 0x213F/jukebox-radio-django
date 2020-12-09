from datetime import timedelta
from urllib.parse import urlencode

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

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

        queue_list = Queue.objects.in_stream(stream)

        format_choices = [("track", "Track"), ("video", "Video")] + list(
            Collection.FORMAT_CHOICES
        )

        print(stream.is_playing, stream.is_paused)

        if not stream.is_playing and not stream.is_paused:
            queue_history = Queue.objects.filter(stream=stream, played_at__isnull=False, deleted_at__isnull=True, is_abstract=False)
        else:
            queue_history = Queue.objects.filter(stream=stream, played_at__isnull=False, is_head=False, deleted_at__isnull=True, is_abstract=False)

        now = timezone.now()
        within_bounds = stream.played_at and now < stream.played_at + timedelta(milliseconds=stream.now_playing.duration_ms)

        return self.template_response(
            request,
            "pages/player.html",
            {
                "queues": queue_list,
                "FORMAT_CHOICES": format_choices,
                "PROVIDER_CHOICES": GLOBAL_PROVIDER_CHOICES,
                "stream_is_playing": stream.is_playing,
                "stream_is_paused": stream.is_paused,
                "stream_queue_history_exists": queue_history.exists(),
                "stream_queue_is_empty": not bool(queue_list),
                "is_over": not within_bounds,
            },
        )
