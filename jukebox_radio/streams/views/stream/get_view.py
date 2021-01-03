from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class StreamGetView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        When a user plays a paused stream.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.select_related('now_playing').get(user=request.user)

        now_playing = {
            "uuid": stream.now_playing.uuid,
            "provider": stream.now_playing.provider,
            "name": stream.now_playing.name,
            "artistName": stream.now_playing.artist_name,
            "albumName": stream.now_playing.album_name,
            "durationMilliseconds": stream.now_playing.duration_ms,
            "externalId": stream.now_playing.external_id,
            "imgUrl": stream.now_playing.img_url,
        } if stream.now_playing else None

        return self.http_response_200({
            "uuid": stream.uuid,
            "nowPlaying": now_playing,
            "isPlaying": stream.is_playing,
            "isPaused": stream.is_paused,
            "playedAt": stream.played_at and int(stream.played_at.timestamp()),
            "pausedAt": stream.paused_at and int(stream.paused_at.timestamp()),
        })
