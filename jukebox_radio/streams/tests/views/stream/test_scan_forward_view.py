import ddf
import pytest

from django.apps import apps


@pytest.mark.django_db
def test_stream_scan_forward_view_assert_request_type(client):
    """
    Assert that /streams/stream/scan-forward/ only allows requests of type
    POST.
    """
    pass


@pytest.mark.django_db
def test_stream_scan_forward_view_request_authentication_required(client):
    """
    If any of the following attempts to access this endpoint, then they should
    be denied access:

        - an unauthenticated user.
        - a user different than the one who wrote the comment.
    """
    pass


@pytest.mark.django_db
def test_stream_scan_forward_view_happy_path(client):
    """
    Move playback forward on a given Stream by N seconds on the current track.
    """
    pass
