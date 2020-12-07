import requests

from django.apps import apps
from django.conf import settings


def refresh_track_external_data(track, user):
    Track = apps.get_model("music", "Track")
    if track.provider == Track.PROVIDER_SPOTIFY:
        return _refresh_track_spotify_data(track, user)
    elif track.provider == Track.PROVIDER_YOUTUBE:
        return _refresh_track_youtube_data(track)
    elif track.provider == Track.PROVIDER_JUKEBOX_RADIO:
        return {}
    else:
        raise ValueError(f"Track has bad provider: {track.uuid}, {track.provider}")


def refresh_collection_external_data(collection, user):
    Collection = apps.get_model("music", "Collection")
    if collection.provider == Collection.PROVIDER_SPOTIFY:
        if collection.format == Collection.FORMAT_ALBUM:
            return _refresh_collection_spotify_album_data(collection, user)
        elif collection.format == Collection.FORMAT_PLAYLIST:
            return _refresh_collection_spotify_playlist_data(collection, user)
    else:
        raise ValueError(f"Track has bad provider: {track.uuid}, {track.provider}")


def _refresh_track_spotify_data(track, user):
    response = requests.get(
        f"https://api.spotify.com/v1/tracks/{track.spotify_id}",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()

    # TODO refresh more data points
    track.duration_ms = response_json["duration_ms"]
    track.save()


def _refresh_track_youtube_data(track):
    params = {
        "part": "snippet,contentDetails",
        "id": track.youtube_id,
        "key": settings.GOOGLE_API_KEY,
    }

    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params=params,
        headers={
            "Content-Type": "application/json",
        },
    )

    response_json = response.json()

    # clean duration
    duration_raw = response_json["items"][0]["contentDetails"]["duration"]

    duration_ms = 0
    mode = None
    val = ''
    for char in duration_raw:
        if char in ['P', 'T']:
            continue

        if char in ['H', 'M', 'S']:
            if char == 'H':
                duration_ms += int(val) * 60 * 60 * 1000
            elif char == 'M':
                duration_ms += int(val) * 60 * 1000
            elif char == 'S':
                duration_ms += int(val) * 60 * 1000
            else:
                raise ValueError(f'Unexpected playtime character: {mode}')

            val = ''
            continue

        val += char

    # TODO refresh more data points
    track.duration_ms = duration_ms
    track.save()


def _refresh_collection_spotify_album_data(collection, user):
    response = requests.get(
        f"https://api.spotify.com/v1/albums/{collection.spotify_id}/tracks",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()
    print(response_json)

    # TODO...
    # items = response_json["items"]
    # data = []
    # for item in items:
    #     data.append(
    #         {
    #             "spotify_uri": item["uri"],
    #             "spotify_duration_ms": item["duration_ms"],
    #             "spotify_name": item["name"],
    #         }
    #     )
    # return data


def _refresh_collection_spotify_playlist_data(collection, user):
    response = requests.get(
        f"https://api.spotify.com/v1/playlists/{collection.spotify_id}",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()
    print(response_json)

    # TODO...
    # items = response_json["tracks"]["items"]
    # data = []
    # for item in items:
    #     data.append(
    #         {
    #             "spotify_uri": item["track"]["uri"],
    #             "spotify_duration_ms": item["track"]["duration_ms"],
    #             "spotify_name": item["track"]["name"],
    #         }
    #     )
    # return data
