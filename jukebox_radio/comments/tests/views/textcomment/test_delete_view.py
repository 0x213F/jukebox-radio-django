import ddf
import pytest

from django.apps import apps


@pytest.mark.django_db
def test_text_comment_delete_view_assert_request_type(client):
    """
    Assert that /comments/text-comment/delete/ only allows requests of type
    DELETE.
    """
    pass


@pytest.mark.django_db
def test_text_comment_delete_view_request_authentication_required(client):
    """
    If any of the following attempts to access this endpoint, then they should
    be denied access:

        - an unauthenticated user.
        - a user different than the one who wrote the comment.
    """
    pass


@pytest.mark.django_db
def test_text_comment_delete_view_happy_path(client):
    """
    Delete a TextComment.
    """
    pass
