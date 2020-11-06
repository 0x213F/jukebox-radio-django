import ddf
import pytest

from django.apps import apps


@pytest.mark.django_db
def test_voice_recording_list_view_assert_request_type(client):
    """
    Assert that /comments/voice-recording/create/ only allows requests of type
    GET.
    """
    pass


@pytest.mark.django_db
def test_voice_recording_list_view_request_authentication_required(client):
    """
    If any of the following attempts to access this endpoint, then they should
    be denied access:

        - an unauthenticated user.
        - a user different than the one who wrote the comment.
    """
    pass


@pytest.mark.django_db
def test_voice_recording_list_view_happy_path(client):
    """
    List all VoiceRecording objects belonging to a (user/ playback) context.
    """
    pass
