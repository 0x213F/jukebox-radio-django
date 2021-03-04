from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class TextCommentModificationCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a TextCommentModification. Typical styles include:

            - Bold
            - Italicize
            - Strikethrough
        """
        TextComment = apps.get_model("comments", "TextComment")
        TextCommentModification = apps.get_model("comments", "TextCommentModification")

        text_comment_uuid = self.param(request, "textCommentUuid")

        # NOTE: This is here to validate that the authenticated user owns the
        #       comment.
        TextComment.objects.get(uuid=text_comment_uuid, user=request.user)

        style = self.param(request, "style")
        ptrs = [
            int(self.param(request, "anchorOffset")),
            int(self.param(request, "focusOffset")),
        ]
        start_ptr = min(ptrs)
        end_ptr = max(ptrs)

        text_comment_modification = TextCommentModification.objects.create_modification(
            user=request.user,
            text_comment_id=text_comment_uuid,
            start_ptr=start_ptr,
            end_ptr=end_ptr,
            style=style,
        )

        return self.http_react_response(
            "textCommentModification/create",
            {
                "textCommentModification": TextCommentModification.objects.serialize(
                    text_comment_modification
                ),
                "textCommentUuid": text_comment_uuid,
            },
        )
