import pytest

from django.apps import apps
from django.urls import reverse

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.django_db
@pytest.mark.parametrize("text_comment_count", [0, 1, 3])
def test_text_comment_list_view_with_various_lengths(
    client,
    django_user_model,
    mocker,
    text_comment_count,
):
    """
    Simple test that lists all text comments for a given track.
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
    text_comments = []
    for idx in range(text_comment_count):
        text_comment = TextComment.objects.create(
            user=user,
            format=TextComment.FORMAT_TEXT,
            text="Hello, world!",
            track_id=track.uuid,
            timestamp_ms=4200 + idx,
        )
        assert not text_comment.deleted_at
        text_comments.append(text_comment)

    # List comments
    response_json = response.json()
    url = reverse("comments:text-comment-list")
    data = {"trackUuid": track.uuid}
    response = client.get(url, data)

    # Verify response
    response_json = response.json()
    assert response_json["system"]["status"] == 200

    assert response_json["redux"]["type"] == "textComment/listSet"
    response_text_comments = response_json["redux"]["payload"]["textComments"]

    # This also asserts that the comments are in the expected order
    assert len(response_text_comments) == text_comment_count
    for idx in range(text_comment_count):
        assert response_text_comments[idx]["uuid"] == str(text_comments[idx].uuid)
