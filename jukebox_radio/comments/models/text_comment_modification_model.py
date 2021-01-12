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

    STYLE_UNDERLINE = "underline"
    STYLE_BOX = "box"
    STYLE_CIRCLE = "circle"
    STYLE_HIGHLIGHT = "highlight"
    STYLE_STRIKE_THROUGH = "strike-through"
    STYLE_CROSSED_OFF = "crossed-off"
    STYLE_BRACKET = "bracket"

    STYLE_CHOICES = (
        (STYLE_UNDERLINE, "Underline"),
        (STYLE_BOX, "Box"),
        (STYLE_CIRCLE, "Circle"),
        (STYLE_HIGHLIGHT, "Highlight"),
        (STYLE_STRIKE_THROUGH, "Strike-through"),
        (STYLE_CROSSED_OFF, "Crossed-off"),
        (STYLE_BRACKET, "Bracket"),
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
