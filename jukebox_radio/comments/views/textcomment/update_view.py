from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core import time as time_util

User = get_user_model()


class TextCommentUpdateView(BaseView, LoginRequiredMixin):

    def delete(self, request, **kwargs):
        """
        Update a TextComment. A side effect is that this clears all related
        TextCommentModification objects.
        """
        TextComment = apps.get_model('comments', 'TextComment')
        TextCommentModification = apps.get_model('comments', 'TextCommentModification')

        text_comment_id = request.DELETE.get('text_comment_id')
        text_comment = (
            TextComment
            .objects
            .get(id=text_comment_id, user=request.user)
        )
        text_comment.text = request.PUT.get('text')
        text_comment.save()

        text_comment_modification_qs = (
            TextCommentModification
            .objects
            .filter(text_comment=text_comment)
        )
        text_comment_modification_qs.delete()

        return self.http_response_200({
            'id': text_comment.id,
            'text': text_comment.text,
        })
