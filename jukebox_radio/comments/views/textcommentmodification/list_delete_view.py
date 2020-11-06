from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class TextCommentModificationListDeleteView(BaseView, LoginRequiredMixin):

    def delete(self, request, **kwargs):
        """
        Delete all TextCommentModification objects that relate to a given
        TextComment.
        """
        text_comment_id = request.PUT.get('text_comment_id')
        text_comment = (
            TextComment
            .objects
            .get(id=text_comment_id, user=request.user)
        )

        text_comment_modification_qs = (
            TextCommentModificatio
            .objects
            .filter(user=request.user, text_comment=text_comment)
        )
        text_comment_modification_ids = text_comment_modification_qs.values_list('id', flat=True)
        text_comment_modification_qs.delete()

        # returns an array of objects
        #     [ { "id": <uuid> }, { "id": <uuid> }, ... ]
        return self.http_response_200(text_comment_modification_ids)
