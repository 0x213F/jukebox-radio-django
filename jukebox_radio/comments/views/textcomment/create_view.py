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

        stream = Stream.objects.get(
            user=request.user
        )

        if not stream.is_playing and not stream.is_paused:
            return self.http_response_400("No track is currently playing in the stream")

        now = time_util.now()
        text = request.POST["text"]
        format = request.POST["format"]
        track_uuid = request.POST["textCommentUuid"]
        timestamp_ms = request.POST["textCommentTimestamp"]

        text_comment = TextComment.objects.create(
            user=request.user,
            format=format,
            text=text,
            track_id=track_uuid,
            timestamp_ms=timestamp_ms,
        )

        return self.http_response_200(TextComment.objects.serialize(text_comment, empty_modifications=True))
