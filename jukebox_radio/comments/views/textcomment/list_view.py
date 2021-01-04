from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class TextCommentListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List TextComment objects that the user has created for a given track.
        """
        TextComment = apps.get_model("comments", "TextComment")
        TextCommentModification = apps.get_model("comments", "TextCommentModification")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing and not stream.is_paused:
            return self.http_response_200([])

        track_uuid = stream.now_playing_id

        text_comment_qs = (
            TextComment.objects.select_related("user", "track")
            .prefetch_related(
                Prefetch(
                    "modifications",
                    queryset=TextCommentModification.objects.filter(
                        deleted_at__isnull=True
                    ).order_by("start_ptr"),
                    to_attr="ordered_modifications",
                )
            )
            .filter(track__uuid=track_uuid, user=request.user, deleted_at__isnull=True)
            .order_by("timestamp_ms")
        )
        text_comments = []
        for text_comment in text_comment_qs:

            text_comment_modifications = []
            for modification in text_comment.ordered_modifications:
                text_comment_modifications.append(
                    {
                        "uuid": modification.uuid,
                        "type": modification.style,
                        "startPtr": modification.start_ptr,
                        "endPtr": modification.end_ptr,
                        "animate": False,
                    }
                )

            text_comments.append(
                {
                    "class": text_comment.__class__.__name__,
                    "uuid": text_comment.uuid,
                    "userUsername": text_comment.user.username,
                    "text": text_comment.text,
                    "trackUuid": text_comment.track.uuid,
                    "timestampMilliseconds": text_comment.timestamp_ms,
                    "modifications": text_comment_modifications,
                }
            )

        return self.http_response_200(text_comments)
