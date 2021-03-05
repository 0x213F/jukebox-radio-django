import pgtrigger
import uuid

from django.apps import apps
from django.db import models
from django.db import transaction

import pghistory
import pgtrigger
from unique_upload import unique_upload

from jukebox_radio.core import time as time_util


class TextCommentModificationManager(models.Manager):
    def serialize(self, text_comment_modification):
        """
        JSON serialize a TextCommentModification.
        """
        if not text_comment_modification:
            return None
        return {
            "uuid": text_comment_modification.uuid,
            "style": text_comment_modification.style,
            "startPtr": text_comment_modification.start_ptr,
            "endPtr": text_comment_modification.end_ptr,
        }

    @pgtrigger.ignore("comments.TextCommentModification:protect_inserts")
    def create_modification(self, *, user, text_comment_id, start_ptr, end_ptr, style):
        """
        Official create interface. In the case where one is trying to create a
        modification that overlaps with any existing modifications, the objects
        are merged into one modification that spans the entire region.
        """
        TextComment = apps.get_model("comments", "TextComment")
        TextCommentModification = apps.get_model("comments", "TextCommentModification")

        text_comment = TextComment.objects.get(uuid=text_comment_id)

        if start_ptr >= end_ptr:
            raise Exception("Invalid pointers")

        if end_ptr > len(text_comment.text):
            raise Exception("Invalid range")

        fields = {
            "user": user,
            "text_comment_id": text_comment_id,
            "start_ptr": start_ptr,
            "end_ptr": end_ptr,
            "style": style,
        }

        container = TextCommentModification.objects.get_container(**fields)
        if container:
            return container, None

        contained = TextCommentModification.objects.filter_contained(**fields)
        archived_list = list(contained)

        lower_overlap = TextCommentModification.objects.get_lower_overlap(**fields)
        upper_overlap = TextCommentModification.objects.get_upper_overlap(**fields)

        with transaction.atomic():
            contained.update(deleted_at=time_util.now())

            # No overlap
            if not lower_overlap and not upper_overlap:
                modification = TextCommentModification.objects.create(
                    user=user,
                    text_comment_id=text_comment_id,
                    start_ptr=start_ptr,
                    end_ptr=end_ptr,
                    style=style,
                )

            # There is a lower overlap
            elif lower_overlap and not upper_overlap:
                lower_overlap.end_ptr = end_ptr
                lower_overlap.save()
                modification = lower_overlap

            # There is an upper overlap
            elif not lower_overlap and upper_overlap:
                upper_overlap.start_ptr = start_ptr
                upper_overlap.save()
                modification = upper_overlap

            # We need to delete one at random - let's delete the higher one.
            else:
                lower_overlap.end_ptr = upper_overlap.end_ptr
                lower_overlap.save()
                upper_overlap.deleted_at = time_util.now()
                upper_overlap.save()
                modification = lower_overlap
                archived_list.append(upper_overlap)

        return modification, archived_list


class TextCommentModificationQuerySet(models.QuerySet):
    def get_container(self, *, user, text_comment_id, start_ptr, end_ptr, style):
        """
        Determines if the given data is already contained within an existing
        modification.
        """
        return self.filter(
            user=user,
            text_comment_id=text_comment_id,
            start_ptr__lte=start_ptr,
            end_ptr__gte=end_ptr,
            style=style,
            deleted_at__isnull=True,
        ).first()

    def filter_contained(self, *, user, text_comment_id, start_ptr, end_ptr, style):
        """
        Filters for modifications inside a given interval.

        NOTE: This filter excludes the bounds.
        """
        return self.filter(
            user=user,
            text_comment_id=text_comment_id,
            start_ptr__gt=start_ptr,
            start_ptr__lt=end_ptr,
            end_ptr__gt=start_ptr,
            end_ptr__lt=end_ptr,
            style=style,
            deleted_at__isnull=True,
        )

    def get_lower_overlap(self, *, user, text_comment_id, start_ptr, end_ptr, style):
        """
        Filters for modifications that overlap on the lower side of the
        interval.
        """
        contained = self.get_container(
            user=user,
            text_comment_id=text_comment_id,
            start_ptr=start_ptr,
            end_ptr=end_ptr,
            style=style,
        )
        if contained:
            return None

        return self.filter(
            user=user,
            text_comment_id=text_comment_id,
            start_ptr__lte=start_ptr,
            end_ptr__gte=start_ptr,
            end_ptr__lte=end_ptr,
            style=style,
            deleted_at__isnull=True,
        ).first()

    def get_upper_overlap(self, *, user, text_comment_id, start_ptr, end_ptr, style):
        """
        Filters for modifications that overlap on the upper side of the
        interval.
        """
        contained = self.get_container(
            user=user,
            text_comment_id=text_comment_id,
            start_ptr=start_ptr,
            end_ptr=end_ptr,
            style=style,
        )
        if contained:
            return None

        return self.filter(
            user=user,
            text_comment_id=text_comment_id,
            start_ptr__gte=start_ptr,
            start_ptr__lte=end_ptr,
            end_ptr__gte=end_ptr,
            style=style,
            deleted_at__isnull=True,
        ).first()


@pgtrigger.register(
    pgtrigger.Protect(name="protect_deletes", operation=pgtrigger.Delete)
)
@pgtrigger.register(
    pgtrigger.Protect(name="protect_inserts", operation=pgtrigger.Insert)
)
class TextCommentModification(models.Model):
    """
    Modifications that change styles on a text comment.
    """

    objects = TextCommentModificationManager.from_queryset(
        TextCommentModificationQuerySet
    )()

    OVERLAP_LOWER = "lower"
    OVERLAP_UPPER = "upper"

    STYLE_BOLD = "bold"
    STYLE_ITALICIZE = "italicize"
    STYLE_STRIKETHROUGH = "strikethrough"
    STYLE_HIGHLIGHT = "highlight"

    STYLE_CHOICES = (
        (STYLE_BOLD, "Bold"),
        (STYLE_ITALICIZE, "Italicize"),
        (STYLE_STRIKETHROUGH, "Strikethrough"),
        (STYLE_HIGHLIGHT, "Highlight"),
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
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.text_comment} ({self.start_ptr}, {self.end_ptr})"
