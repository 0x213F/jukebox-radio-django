from datetime import timedelta

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import QueryDict

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core import time as time_util

User = get_user_model()


class TextCommentCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a TextComment.
        """
        TextComment = apps.get_model("comments", "TextComment")
        Stream = apps.get_model("streams", "Stream")

        print('!!!!')

        now = time_util.now()

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        end_of_the_track = stream.played_at + timedelta(milliseconds=stream.now_playing.duration_ms)
        track_is_over = stream.now_playing and now > end_of_the_track
        if not stream.now_playing or track_is_over:
            return self.http_response_400("No track is currently playing in the stream")

        text = request.POST.get("text")
        text_comment = TextComment.objects.create(
            user=request.user,
            text=text,
            track=stream.now_playing,
            timestamp_ms=time_util.ms(now - stream.played_at),
        )

        return self.http_response_200(
            {
                "uuid": text_comment.uuid,
                "userUsername": text_comment.user.username,
                "text": text_comment.text,
                "trackId": text_comment.track_id,
                "timestampMilliseconds": text_comment.timestamp_ms,
            }
        )
