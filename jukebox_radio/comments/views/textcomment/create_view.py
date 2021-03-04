from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class TextCommentCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a TextComment.
        """
        TextComment = apps.get_model("comments", "TextComment")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        text = self.param(request, "text")
        format = self.param(request, "format")
        track_uuid = self.param(request, "textCommentUuid")
        timestamp_ms = self.param(request, "textCommentTimestamp")

        text_comment = TextComment.objects.create(
            user=request.user,
            format=format,
            text=text,
            track_id=track_uuid,
            timestamp_ms=timestamp_ms,
        )

        return self.http_response_200(
            TextComment.objects.serialize(text_comment, empty_modifications=True)
        )
