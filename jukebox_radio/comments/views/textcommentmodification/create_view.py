from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class TextCommentModificationCreateView(BaseView, LoginRequiredMixin):

    def put(self, request, **kwargs):
        """
        Create a TextCommentModification. Typical styles include:

            - Highlight
            - Strikethrough
            - Underline
        """
        text_comment_id = request.PUT.get('text_comment_id')
        text_comment = (
            TextComment
            .objects
            .get(id=text_comment_id, user=request.user)
        )

        start_ptr = request.PUT.get('start_ptr')
        end_ptr = request.PUT.get('end_ptr')
        style = request.PUT.get('style')

        text_comment_modification = TextCommentModification.objects.create(
            user=request.user,
            text_comment=text_comment,
            start_ptr=start_ptr,
            end_ptr=end_ptr,
            style=style,
        )

        return self.http_response_200({
            'id': text_comment_modification.id,
            'user__username': text_comment_modification.user.username,
            'text_comment_id': text_comment_modification.text_comment_id,
            'start_ptr': start_ptr,
            'end_ptr': end_ptr,
            'style': style,
        })
