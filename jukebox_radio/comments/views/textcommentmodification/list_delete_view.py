from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core import time as time_util

User = get_user_model()


class TextCommentModificationListDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Delete all TextCommentModification objects that relate to a given
        TextComment.
        """
        TextComment = apps.get_model("comments", "TextComment")
        TextCommentModification = apps.get_model("comments", "TextCommentModification")

        text_comment_uuid = request.POST["textCommentUuid"]

        text_comment_modification_qs = TextCommentModification.objects.filter(
            user=request.user, text_comment_id=text_comment_uuid
        )
        text_comment_modification_qs.update(deleted_at=time_util.now())

        return self.http_response_200()
