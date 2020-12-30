import json

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class TextCommentDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Delete a TextComment.
        """
        TextComment = apps.get_model("comments", "TextComment")

        text_comment_uuid = request.POST["textCommentUuid"]
        text_comment = TextComment.objects.get(
            uuid=text_comment_uuid, user=request.user
        )
        text_comment.archive()

        return self.http_response_200()
