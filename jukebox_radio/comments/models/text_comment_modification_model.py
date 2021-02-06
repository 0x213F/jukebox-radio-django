import pgtrigger
import uuid

from django.db import models

import pghistory
import pgtrigger
from unique_upload import unique_upload

from jukebox_radio.core import time as time_util


class TextCommentModificationManager(models.Manager):
    def serialize(self, text_comment_modification, animate=False):
        return {
            "uuid": text_comment_modification.uuid,
            "type": text_comment_modification.style,
            "startPtr": text_comment_modification.start_ptr,
            "endPtr": text_comment_modification.end_ptr,
            "animate": animate,
        }


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
class TextCommentModification(models.Model):

    objects = TextCommentModificationManager()

    STYLE_BOLD = "bold"
    STYLE_ITALICIZE = "italicize"
    STYLE_STRIKETHROUGH = "strikethrough"

    STYLE_CHOICES = (
        (STYLE_BOLD, "Bold"),
        (STYLE_ITALICIZE, "Italicize"),
        (STYLE_STRIKETHROUGH, "Strikethrough"),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    text_comment = models.ForeignKey(
        "comments.TextComment",
        related_name="modifications",
        on_delete=models.CASCADE,
    )

    start_ptr = models.PositiveSmallIntegerField()
    end_ptr = models.PositiveSmallIntegerField()
    style = models.CharField(max_length=32, choices=STYLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.text_comment} ({self.start_ptr}, {self.end_ptr})"
