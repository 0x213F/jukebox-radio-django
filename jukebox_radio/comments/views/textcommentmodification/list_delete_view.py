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
        TextComment = apps.get_model('comments', 'TextComment')
        TextCommentModification = apps.get_model('comments', 'TextCommentModification')

        text_comment_uuid = request.PUT.get('textCommentUuid')
        text_comment = (
            TextComment
            .objects
            .get(uuid=text_comment_uuid, user=request.user)
        )

        text_comment_modification_qs = (
            TextCommentModificatio
            .objects
            .filter(user=request.user, text_comment=text_comment)
        )
        text_comment_modification_uuids = text_comment_modification_qs.values_list('uuid', flat=True)
        text_comment_modification_qs.delete()

        # returns an array of objects
        #     [ { "uuid": <uuid> }, { "uuid": <uuid> }, ... ]
        return self.http_response_200(text_comment_modification_uuids)
