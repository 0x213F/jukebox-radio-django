from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class TextCommentListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List TextComment objects that the user has created for whatever is now
        playing.
        """
        TextComment = apps.get_model("comments", "TextComment")
        TextCommentModification = apps.get_model("comments", "TextCommentModification")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing and not stream.is_paused:
            return self.http_react_response(
                "textComment/listSet",
                {
                    "textComments": [],
                },
            )

        track_uuid = stream.now_playing.track_id

        text_comment_qs = TextComment.objects.notepad_filter(track_uuid, request.user)

        text_comments = []
        for text_comment in text_comment_qs:
            text_comments.append(TextComment.objects.serialize(text_comment))

        return self.http_react_response(
            "textComment/listSet",
            {
                "textComments": text_comments,
            },
        )
