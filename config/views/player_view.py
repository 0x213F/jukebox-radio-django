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

        if not request.user.is_authenticated:
            return self.redirect_response('/')

        stream, _ = Stream.objects.get_or_create(user=request.user)

        queue_list = Queue.objects.in_stream(stream)

        format_choices = [("track", "Track"), ("video", "Video")] + list(
            Collection.FORMAT_CHOICES
        )

        if not stream.is_playing and not stream.is_paused:
            queue_history = Queue.objects.filter(stream=stream, played_at__isnull=False, deleted_at__isnull=True, is_abstract=False)
        else:
            queue_history = Queue.objects.filter(stream=stream, played_at__isnull=False, is_head=False, deleted_at__isnull=True, is_abstract=False)

        now = timezone.now()
        within_bounds = stream.played_at and now < stream.played_at + timedelta(milliseconds=stream.now_playing.duration_ms)

        try:
            if not stream.paused_at:
                progress = (timezone.now() - stream.played_at) / timedelta(milliseconds=stream.now_playing.duration_ms) * 100
            else:
                progress = (stream.paused_at - stream.played_at) / timedelta(milliseconds=stream.now_playing.duration_ms) * 100
        except Exception:
            progress = 0

        print(stream.is_playing, stream.is_paused, not within_bounds)

        return self.template_response(
            request,
            "pages/player.html",
            {
                "queues": queue_list,
                "FORMAT_CHOICES": format_choices,
                "PROVIDER_CHOICES": GLOBAL_PROVIDER_CHOICES,
                "stream_now_playing": stream.now_playing,
                "stream_is_playing": stream.is_playing,
                "stream_is_paused": stream.is_paused,
                "stream_queue_history_exists": queue_history.exists(),
                "stream_queue_is_empty": not bool(queue_list),
                "is_over": not within_bounds,
                "progress": progress,
            },
        )
