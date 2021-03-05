import pytest

from django.apps import apps
from django.urls import reverse

import pgtrigger

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.skip()
@pytest.mark.django_db
@pytest.mark.parametrize("text_comment_modification_count", [0, 1, 3])
def test_text_comment_modification_list_delete_view_happy_path(
    client,
    django_user_model,
    mocker,
    text_comment_modification_count,
):
    """
    Assert that /comments/text-comment/create/ only allows requests of type
    PUT.
    """
    TextComment = apps.get_model("comments", "TextComment")
    TextCommentModification = apps.get_model("comments", "TextCommentModification")

    # Initialize user
    credentials = {
        "username": "username",
        "password": "password",
    }
    user = django_user_model.objects.create_user(**credentials)

    # Login
    response = client.login(**credentials)

    # Initialize stream
    url = reverse("streams:stream-initialize")
    response = client.post(url)

    # Create a track object
    track = create_test_track()

    # Create comment
    text_comment = TextComment.objects.create(
        user=user,
        format=TextComment.FORMAT_TEXT,
        text="Hello, world!",
        track_id=track.uuid,
        timestamp_ms=4200,
    )
    assert not text_comment.deleted_at

    # Create text comment modification
    with pgtrigger.ignore("comments.TextCommentModification:protect_inserts"):
        text_comment_modifications = []
        for idx in range(text_comment_modification_count):
            text_comment_modification = TextCommentModification.objects.create(
                user=user,
                text_comment=text_comment,
                start_ptr=(idx * 2),
                end_ptr=(idx * 2 + 2),
                style=TextCommentModification.STYLE_BOLD,
            )
            assert not text_comment_modification.deleted_at
            text_comment_modifications.append(text_comment_modification)

    # Create text comment modification
    url = reverse("comments:text-comment-modification-list-delete")
    data = {
        "textCommentUuid": text_comment.uuid,
    }
    response = client.post(url, data)

    # Verify response
    response_json = response.json()
    assert response_json["system"]["status"] == 200
    assert False

    for text_comment_modification in text_comment_modifications:
        text_comment_modification.refresh_from_db()
        assert text_comment_modification.deleted_at
