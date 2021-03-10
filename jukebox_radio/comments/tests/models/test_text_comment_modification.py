import pgtrigger
import pytest
from django.apps import apps

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_ptr, end_ptr, expected_result",
    [
        # Overlapping
        (3, 6, True),
        (4, 7, True),
        (4, 6, True),
        (3, 7, True),
        # Below
        (2, 7, False),
        (2, 6, False),
        (0, 3, False),
        (0, 2, False),
        # Above
        (3, 8, False),
        (4, 8, False),
        (7, 10, False),
        (8, 10, False),
    ],
)
def test_text_comment_modification_get_container(
    django_user_model,
    start_ptr,
    end_ptr,
    expected_result,
):
    """
    Verify finding the "container" interval with all possible combinations. The
    container modification would be an existing modification that is the same
    or larger than the proposed one.
    """
    TextComment = apps.get_model("comments", "TextComment")
    TextCommentModification = apps.get_model("comments", "TextCommentModification")

    # Initialize user
    credentials = {
        "username": "username",
        "password": "password",
    }
    user = django_user_model.objects.create_user(**credentials)

    # Create a track object
    track = create_test_track()

    text_comment = TextComment.objects.create(
        user=user,
        format=TextComment.FORMAT_TEXT,
        text="0123456789",
        track_id=track.uuid,
        timestamp_ms=4200,
    )

    style = TextCommentModification.STYLE_BOLD
    with pgtrigger.ignore("comments.TextCommentModification:protect_inserts"):
        TextCommentModification.objects.create(
            user=user,
            text_comment_id=text_comment.uuid,
            start_ptr=3,
            end_ptr=7,
            style=style,
        )

    contained = TextCommentModification.objects.get_container(
        user=user,
        text_comment_id=text_comment.uuid,
        start_ptr=start_ptr,
        end_ptr=end_ptr,
        style=style,
    )
    assert bool(contained) == expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_ptr, end_ptr, expected_result",
    [
        # Overlapping
        (3, 6, False),
        (4, 7, False),
        (4, 6, False),
        (3, 7, False),
        # Below
        (2, 7, False),
        (2, 6, False),
        (0, 3, False),
        (0, 2, False),
        # Above
        (3, 8, True),
        (4, 8, True),
        (7, 10, True),
        (8, 10, False),
    ],
)
def test_text_comment_modification_get_lower_overlap(
    django_user_model,
    start_ptr,
    end_ptr,
    expected_result,
):
    """
    Verify each case validate expected lower bound overlap.
    """
    TextComment = apps.get_model("comments", "TextComment")
    TextCommentModification = apps.get_model("comments", "TextCommentModification")

    # Initialize user
    credentials = {
        "username": "username",
        "password": "password",
    }
    user = django_user_model.objects.create_user(**credentials)

    # Create a track object
    track = create_test_track()

    text_comment = TextComment.objects.create(
        user=user,
        format=TextComment.FORMAT_TEXT,
        text="0123456789",
        track_id=track.uuid,
        timestamp_ms=4200,
    )

    style = TextCommentModification.STYLE_BOLD
    with pgtrigger.ignore("comments.TextCommentModification:protect_inserts"):
        TextCommentModification.objects.create(
            user=user,
            text_comment_id=text_comment.uuid,
            start_ptr=3,
            end_ptr=7,
            style=style,
        )

    lower_overlap = TextCommentModification.objects.get_lower_overlap(
        user=user,
        text_comment_id=text_comment.uuid,
        start_ptr=start_ptr,
        end_ptr=end_ptr,
        style=style,
    )
    assert bool(lower_overlap) == expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_ptr, end_ptr, expected_result",
    [
        # Overlapping
        (3, 6, False),
        (4, 7, False),
        (4, 6, False),
        (3, 7, False),
        # Below
        (2, 7, True),
        (2, 6, True),
        (0, 3, True),
        (0, 2, False),
        # Above
        (3, 8, False),
        (4, 8, False),
        (7, 10, False),
        (8, 10, False),
    ],
)
def test_text_comment_modification_get_upper_overlap(
    django_user_model,
    start_ptr,
    end_ptr,
    expected_result,
):
    """
    Verify each case validate expected upper bound overlap.
    """
    TextComment = apps.get_model("comments", "TextComment")
    TextCommentModification = apps.get_model("comments", "TextCommentModification")

    # Initialize user
    credentials = {
        "username": "username",
        "password": "password",
    }
    user = django_user_model.objects.create_user(**credentials)

    # Create a track object
    track = create_test_track()

    text_comment = TextComment.objects.create(
        user=user,
        format=TextComment.FORMAT_TEXT,
        text="0123456789",
        track_id=track.uuid,
        timestamp_ms=4200,
    )

    style = TextCommentModification.STYLE_BOLD
    with pgtrigger.ignore("comments.TextCommentModification:protect_inserts"):
        TextCommentModification.objects.create(
            user=user,
            text_comment_id=text_comment.uuid,
            start_ptr=3,
            end_ptr=7,
            style=style,
        )

    upper_overlap = TextCommentModification.objects.get_upper_overlap(
        user=user,
        text_comment_id=text_comment.uuid,
        start_ptr=start_ptr,
        end_ptr=end_ptr,
        style=style,
    )
    assert bool(upper_overlap) == expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ptrs, modification_count, archived_count",
    [
        ([], 1, 0),
        ([(4, 6)], 1, 1),
        ([(2, 8)], 1, 0),
        ([(2, 4)], 1, 0),
        ([(6, 8)], 1, 0),
        ([(2, 4), (6, 8)], 1, 1),
        ([(1, 2), (8, 9)], 3, 0),
    ],
)
def test_text_comment_modification_create_modification(
    django_user_model, ptrs, modification_count, archived_count
):
    """
    Test the custom create method. When creating, existing overlapping objects
    should be condensed.
    """
    TextComment = apps.get_model("comments", "TextComment")
    TextCommentModification = apps.get_model("comments", "TextCommentModification")

    # Initialize user
    credentials = {
        "username": "username",
        "password": "password",
    }
    user = django_user_model.objects.create_user(**credentials)

    # Create a track object
    track = create_test_track()

    text_comment = TextComment.objects.create(
        user=user,
        format=TextComment.FORMAT_TEXT,
        text="0123456789",
        track_id=track.uuid,
        timestamp_ms=4200,
    )

    style = TextCommentModification.STYLE_BOLD
    with pgtrigger.ignore("comments.TextCommentModification:protect_inserts"):
        for (start_ptr, end_ptr) in ptrs:
            TextCommentModification.objects.create(
                user=user,
                text_comment_id=text_comment.uuid,
                start_ptr=start_ptr,
                end_ptr=end_ptr,
                style=style,
            )

    TextCommentModification.objects.create_modification(
        user=user,
        text_comment_id=text_comment.uuid,
        start_ptr=3,
        end_ptr=7,
        style=style,
    )

    actual_modification_count = TextCommentModification.objects.filter(
        deleted_at__isnull=True
    ).count()
    assert actual_modification_count == modification_count

    actual_archived_count = TextCommentModification.objects.filter(
        deleted_at__isnull=False
    ).count()
    assert actual_archived_count == archived_count
