import pytest
from django.apps import apps
from django.urls import reverse

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.django_db
def test_text_comment_modification_create_view_happy_path(
    client,
    django_user_model,
    mocker,
):
    """
    Simple test that lists all text comments for a given track.
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
    url = reverse("comments:text-comment-modification-create")
    data = {
        "textCommentUuid": text_comment.uuid,
        "style": TextCommentModification.STYLE_BOLD,
        "anchorOffset": 0,
        "focusOffset": 5,
    }
    response = client.post(url, data)

    # Verify response
    response_json = response.json()
    assert response_json["system"]["status"] == 200

    assert response_json["redux"]["type"] == "textCommentModification/create"
    payload = response_json["redux"]["payload"]

    assert payload["textCommentUuid"] == str(text_comment.uuid)

    # Meaning, no modifications were deleted
    assert not payload["textCommentModifications"]["deleted"]

    TextCommentModification.objects.get(
        uuid=payload["textCommentModifications"]["modified"]["uuid"],
        user=user,
        text_comment=text_comment,
        start_ptr=data["anchorOffset"],
        end_ptr=data["focusOffset"],
        style=data["style"],
        deleted_at__isnull=True,
    )
