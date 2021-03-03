import ddf
import pytest

from django.apps import apps
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.django_db
def test_stream_pause_track_view_happy_path(
    client, django_user_model, mocker,
):
    """
    Assert that /comments/text-comment/create/ only allows requests of type
    PUT.
    """
    Stream = apps.get_model('streams', 'Stream')

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

    # Get user's stream and verify its state
    stream = Stream.objects.get(user=user)
    assert not stream.is_playing
    assert not stream.is_paused

    # Start playback
    url = reverse('streams:stream-next-track')
    data = {'nowPlayingTotalDurationMilliseconds': 'null', 'isPlanned': 'false'}
    response = client.post(url, data)

    # Verify expected state
    stream.refresh_from_db()
    assert stream.is_playing
    assert not stream.is_paused

    # Pause playback
    url = reverse('streams:stream-pause')
    data = { 'nowPlayingTotalDurationMilliseconds': track.duration_ms }
    response = client.post(url, data)

    # Verify response
    response_json = response.json()
    assert response_json['system']['status'] == 200

    # Verify expected state
    stream.refresh_from_db()
    assert not stream.is_playing
    assert stream.is_paused
