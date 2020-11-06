from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core import time as time_util

User = get_user_model()


class TextCommentDeleteView(BaseView, LoginRequiredMixin):

    def delete(self, request, **kwargs):
        """
        Delete a TextComment.
        """
        TextComment = apps.get_model('comments', 'TextComment')

        text_comment_id = request.DELETE.get('text_comment_id')

        text_comment = (
            TextComment
            .objects
            .get(id=text_comment_id, user=request.user)
        )
        text_comment.delete()

        return self.http_response_200({
            'id': text_comment.id,
        })
