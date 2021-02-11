import pgtrigger
import uuid

from django.apps import apps
from django.db import models
from django.db.models import Prefetch

import pghistory
import pgtrigger
from unique_upload import unique_upload

from jukebox_radio.core import time as time_util


class TextCommentManager(models.Manager):
    def serialize(self, text_comment, empty_modifications=False):
        TextCommentModification = apps.get_model("comments", "TextCommentModification")

        text_comment_modifications = []
        if empty_modifications:
            # NOTE: "ordered_modifications" is a property defined by
            #       "prefetch_related" in "notepad_filter"
            for modification in text_comment.ordered_modifications:
                text_comment_modifications.append(
                    TextCommentModification.objects.serialize(modification)
                )

        return {
            "class": text_comment.__class__.__name__,
            "uuid": text_comment.uuid,
            "userUsername": text_comment.user.username,
            "format": text_comment.format,
            "text": text_comment.text,
            "trackUuid": text_comment.track.uuid,
            "timestampMilliseconds": text_comment.timestamp_ms,
            "modifications": text_comment_modifications,
        }


class TextCommentQuerySet(models.QuerySet):
    def notepad_filter(self, track_uuid, user):
        TextCommentModification = apps.get_model("comments", "TextCommentModification")
        return (
            self.select_related("user", "track")
            .prefetch_related(
                Prefetch(
                    "modifications",
                    queryset=TextCommentModification.objects.filter(
                        deleted_at__isnull=True
                    ).order_by("start_ptr"),
                    to_attr="ordered_modifications",
                )
            )
            .filter(track__uuid=track_uuid, user=user, deleted_at__isnull=True)
            .order_by("timestamp_ms")
        )


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
@pghistory.track(pghistory.Snapshot("text_comment.snapshot"))
class TextComment(models.Model):

    FORMAT_TEXT = "text"
    FORMAT_ABC_NOTATION = "abc_notation"

    FORMAT_CHOICES = (
        (FORMAT_TEXT, "Text"),
        (FORMAT_ABC_NOTATION, "ABC Notation"),
    )

    objects = TextCommentManager.from_queryset(TextCommentQuerySet)()

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    format = models.CharField(max_length=32, choices=FORMAT_CHOICES)

    text = models.TextField()
    track = models.ForeignKey("music.Track", on_delete=models.CASCADE)
    timestamp_ms = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.user}] {self.text}"

    def archive(self):
        self.deleted_at = time_util.now()
        self.save()
