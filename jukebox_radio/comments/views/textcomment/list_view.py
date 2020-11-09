from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class TextCommentListView(BaseView, LoginRequiredMixin):

    def get(self, request, **kwargs):
        """
        List TextComment objects that the user has created for a given track.
        """
        TextComment = apps.get_model('comments', 'TextComment')

        track_uuid = request.GET.get('trackUuid')

        text_comment_qs = (
            TextComment
            .objects
            .select_related('user', 'track')
            .filter(track__uuid=track_uuid, user=request.user)
            .order_by('created_at')
        )
        text_comments = []
        for text_comment in text_comment_qs:
            text_comment.append({
                'uuid': text_comment.uuid,
                'userUsername': text_comment.user.username,
                'text': text_comment.text,
                'trackUuid': text_comment.track.uuid,
                'timestampMilliseconds': text_comment.timestamp_ms,
            })

        return self.http_response_200(text_comments)
