import pytest
from django.apps import apps
from django.urls import reverse

from jukebox_radio.music.tests.factory import create_test_track


@pytest.mark.django_db
def test_marker_create_view_happy_path(
    client,
    django_user_model,
    mocker,
):
    """
    Simple case for creating a text comment through the API.
    """
    Marker = apps.get_model("streams", "Marker")

    # Initialize user
    credentials = {"username": "username", "password": "password"}
    user = django_user_model.objects.create_user(**credentials)

    # Login
    response = client.login(**credentials)

    # Initialize stream
    url = reverse("streams:stream-initialize")
    response = client.post(url)

    # Create a track object
    track = create_test_track()

    # Create comment
    url = reverse("streams:marker-create")
    data = {
        "trackUuid": str(track.uuid),
        "timestampMilliseconds": 420,
        "queueUuid": "foobarbaz",  # Yes, this is on purpose!
        "name": "fooname",
    }
    response = client.post(url, data)

    # Verify response
    response_json = response.json()
    assert response_json["system"]["status"] == 200

    payload = response_json["redux"]["payload"]
    marker = Marker.objects.get(uuid=payload["marker"]["uuid"])
    assert payload["marker"]["uuid"] == str(marker.uuid)
    assert payload["marker"]["name"] == data["name"]
    assert payload["marker"]["trackUuid"] == data["trackUuid"]
    # cast json response to int to match original payload
    assert (
        int(payload["marker"]["timestampMilliseconds"]) == data["timestampMilliseconds"]
    )

    # Assert database entry
    assert marker.user_id == user.id
    assert marker.name == data["name"]
    assert str(marker.track_id) == data["trackUuid"]
    assert marker.timestamp_ms == data["timestampMilliseconds"]
    assert not marker.deleted_at
