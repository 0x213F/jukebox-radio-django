import ddf
import pytest

from django.apps import apps


@pytest.mark.django_db
def test_stream_skip_track_view_assert_request_type(client):
    """
    Assert that /streams/stream/skip-track/ only allows requests of type POST.
    """
    pass


@pytest.mark.django_db
def test_stream_skip_track_view_request_authentication_required(client):
    """
    If any of the following attempts to access this endpoint, then they should
    be denied access:

        - an unauthenticated user.
        - a user different than the one who wrote the comment.
    """
    pass


@pytest.mark.django_db
def test_stream_skip_track_view_happy_path(client):
    """
    Skip playback on a given Stream to the next track in queue.
    """
    pass
