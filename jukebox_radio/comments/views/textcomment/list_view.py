from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class TextCommentListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List TextComment objects that belong to the authenticated user for a
        given track.
        """
        TextComment = apps.get_model("comments", "TextComment")

        track_uuid = self.param(request, "trackUuid")
        text_comment_qs = TextComment.objects.context_filter(track_uuid, request.user)

        text_comments = []
        for text_comment in text_comment_qs:
            text_comments.append(TextComment.objects.serialize(text_comment))

        return self.http_react_response(
            "textComment/listSet",
            {"textComments": text_comments, "trackUuid": track_uuid},
        )
