import pytest

from django.apps import apps
from django.urls import reverse

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.skip()
@pytest.mark.django_db
def test_text_comment_delete_view_happy_path(
    client,
    django_user_model,
    mocker,
):
    """
    Simple case for deleting (archiving) a text comment through the API.
    """
    TextComment = apps.get_model("comments", "TextComment")

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

    # Delete comment
    url = reverse("comments:text-comment-delete")
    data = {
        "textCommentUuid": text_comment.uuid,
    }
    response = client.post(url, data)

    # Verify response
    response_json = response.json()
    assert response_json["system"]["status"] == 200
    assert False

    text_comment.refresh_from_db()
    assert text_comment.deleted_at
