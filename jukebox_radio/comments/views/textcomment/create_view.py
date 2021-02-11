import json
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

        stream = Stream.objects.select_related("now_playing__track").get(
            user=request.user
        )

        if not stream.is_playing and not stream.is_paused:
            return self.http_response_400("No track is currently playing in the stream")

        now = time_util.now()
        text = request.POST["text"]
        format = request.POST["format"]
        now_playing_track = stream.now_playing.track
        timestamp_ms = (
            time_util.ms(now - stream.started_at)
            if stream.is_playing
            else time_util.ms(stream.started_at - stream.paused_at)
        )

        text_comment = TextComment.objects.create(
            user=request.user,
            format=format,
            text=text,
            track=now_playing_track,
            timestamp_ms=timestamp_ms,
        )

        return self.http_response_200(
            {
                "class": text_comment.__class__.__name__,
                "uuid": text_comment.uuid,
                "userUsername": text_comment.user.username,
                "text": text_comment.text,
                "trackUuid": text_comment.track_id,
                "timestampMilliseconds": text_comment.timestamp_ms,
                "modifications": [],
            }
        )
