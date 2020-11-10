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
        TextComment = apps.get_model("comments", "TextComment")
        TextCommentModification = apps.get_model("comments", "TextCommentModification")

        text_comment_uuid = request.PUT.get("textCommentUuid")
        text_comment = TextComment.objects.get(
            uuid=text_comment_uuid, user=request.user
        )

        start_ptr = request.PUT.get("startPtr")
        end_ptr = request.PUT.get("endPtr")
        style = request.PUT.get("style")

        text_comment_modification = TextCommentModification.objects.create(
            user=request.user,
            text_comment=text_comment,
            start_ptr=start_ptr,
            end_ptr=end_ptr,
            style=style,
        )

        return self.http_response_200(
            {
                "uuid": text_comment_modification.uuid,
                "userUsername": text_comment_modification.user.username,
                "textCommentId": text_comment_modification.text_comment_id,
                "startPtr": start_ptr,
                "endPtr": end_ptr,
                "style": style,
            }
        )
