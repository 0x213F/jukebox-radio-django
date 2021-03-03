from django.apps import apps


def create_test_track():
    """
    Just a random track I took out of the database that can be used for
    testing.
    """
    Track = apps.get_model("music", "Track")
    return Track.objects.create(
        format=Track.FORMAT_TRACK,
        provider=Track.PROVIDER_SPOTIFY,
        name="Say My Name (feat. Zyra)",
        artist_name="ODESZA, Zyra",
        album_name="In Return",
        duration_ms=262956,
        external_id="spotify:track:1LeItUMezKA1HdCHxYICed",
        img_url="https://i.scdn.co/image/ab67616d0000b2732d86f76b4e373e312f3662b5",
    )
