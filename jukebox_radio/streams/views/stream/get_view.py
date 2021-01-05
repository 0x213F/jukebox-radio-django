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

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        now_playing = (
            {
                "uuid": stream.now_playing.track.uuid,
                "provider": stream.now_playing.track.provider,
                "name": stream.now_playing.track.name,
                "artistName": stream.now_playing.track.artist_name,
                "albumName": stream.now_playing.track.album_name,
                "durationMilliseconds": stream.now_playing.track.duration_ms,
                "externalId": stream.now_playing.track.external_id,
                "imgUrl": stream.now_playing.track.img_url,
            }
            if stream.now_playing_id and stream.now_playing.track_id
            else None
        )

        return self.http_response_200(
            {
                "uuid": stream.uuid,
                "nowPlaying": now_playing,
                "isPlaying": stream.is_playing,
                "isPaused": stream.is_paused,
                "playedAt": stream.started_at and int(stream.started_at.timestamp()),
                "pausedAt": stream.paused_at and int(stream.paused_at.timestamp()),
            }
        )
