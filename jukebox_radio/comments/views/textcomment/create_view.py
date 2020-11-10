from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core import time as time_util

User = get_user_model()


class TextCommentCreateView(BaseView, LoginRequiredMixin):
    def put(self, request, **kwargs):
        """
        Create a TextComment.
        """
        TextComment = apps.get_model("comments", "TextComment")
        Stream = apps.get_model("streams", "Stream")

        now = time_util.nowutc()
        stream = Stream.objects.select_related("now_playing").get(user=request.user)
        text = request.PUT.get("text")
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
