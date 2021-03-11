from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView


class TextCommentModificationListDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Delete (archive) all TextCommentModification objects that related to a
        given TextComment. In practice, this is like "wiping" the comment
        clean.
        """
        TextCommentModification = apps.get_model("comments", "TextCommentModification")

        text_comment_uuid = self.param(request, "textCommentUuid")

        text_comment_modification_qs = TextCommentModification.objects.filter(
            user=request.user, text_comment_id=text_comment_uuid
        )
        text_comment_modification_qs.update(deleted_at=time_util.now())

        return self.http_react_response(
            "textComment/clearModifications",
            {
                "textCommentUuid": text_comment_uuid,
            },
        )
