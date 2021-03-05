from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class TextCommentDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Delete (archive) a TextComment.
        """
        TextComment = apps.get_model("comments", "TextComment")

        text_comment_uuid = self.param(request, "textCommentUuid")
        text_comment = TextComment.objects.get(
            uuid=text_comment_uuid, user=request.user
        )
        text_comment.archive()

        return self.http_react_response(
            "textComment/delete",
            {"textCommentUuid": text_comment_uuid},
        )
