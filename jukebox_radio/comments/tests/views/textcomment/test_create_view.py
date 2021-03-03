import ddf
import pytest

from django.apps import apps
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.django_db
def test_text_comment_create_view_assert_request_type(
    client, django_user_model, mocker,
):
    """
    Assert that /comments/text-comment/create/ only allows requests of type
    PUT.
    """
    TextComment = apps.get_model('comments', 'TextComment')

    # Initialize user
    credentials = {
        "username": "username",
        "password": "password",
    }
    user = django_user_model.objects.create_user(**credentials)

    # Login
    response = client.login(**credentials)

    # Initialize stream
    url = reverse('streams:stream-initialize')
    response = client.post(url)

    # Create a track object
    track = create_test_track()

    # Mock out a function that calls external APIs
    mocker.patch(
        (
            'jukebox_radio.streams.views.queue.create_view.'
            'refresh_track_external_data'
        ),
        return_value=True
    )

    # Add that track to the queue
    url = reverse('streams:queue-create')
    data = {'className': 'Track', 'genericUuid': track.uuid}
    response = client.post(url, data)

    # Start playback
    url = reverse('streams:stream-next-track')
    data = {'nowPlayingTotalDurationMilliseconds': 'null', 'isPlanned': 'false'}
    response = client.post(url, data)

    # Create comment
    url = reverse('comments:text-comment-create')
    data = {
        'text': 'Hello, world!',
        'format': TextComment.FORMAT_TEXT,
        'textCommentUuid': track.uuid,
        'textCommentTimestamp': 4200,
    }
    response = client.post(url, data)

    # Verify response
    response_json = response.json()

    assert response_json['system']['status'] == 200

    text_comment_uuid = response_json['data']['uuid']
    text_comment = TextComment.objects.get(uuid=text_comment_uuid)
    assert text_comment.text == data['text']
    assert text_comment.format == data['format']
    assert text_comment.track_id == data['textCommentUuid']
    assert text_comment.timestamp_ms == data['textCommentTimestamp']
