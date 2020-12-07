import requests

from django.apps import apps


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
        "key": secrets.GOOGLE_API_KEY,
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
    print(duration_raw)

    # TODO hours too
    duration_minutes_raw = duration_raw[2:].split("M")[0] if "M" in duration_raw else 0
    duration_seconds_raw = (
        duration_raw.split("M")[1][:-1]
        if "M" in duration_raw
        else duration_raw[2:][:-1]
    )
    duration_ms = (60 * 1000 * int(duration_minutes_raw)) + (
        1000 * int(duration_seconds_raw)
    )

    # TODO refresh more data points
    track.duration_ms = duration_ms
    track.save()


def _refresh_collection_spotify_album_data(collection, user):
    spotify_id = spotify_uri[14:]
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
