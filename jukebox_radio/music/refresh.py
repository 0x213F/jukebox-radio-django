from django.apps import apps
from django.conf import settings

from jukebox_radio.core import time as time_util
from jukebox_radio.core.utils import generate_apple_music_token
from jukebox_radio.networking.actions import make_request


def refresh_track_external_data(track, user):
    Track = apps.get_model("music", "Track")
    if track.provider == Track.PROVIDER_SPOTIFY:
        return _refresh_track_spotify_data(track, user)
    elif track.provider == Track.PROVIDER_YOUTUBE:
        return _refresh_track_youtube_data(track)
    elif track.provider == Track.PROVIDER_JUKEBOX_RADIO:
        return {}
    elif track.provider == Track.PROVIDER_APPLE_MUSIC:
        return {}
    elif track.provider == Track.PROVIDER_AUDIUS:
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
    elif collection.provider == Collection.PROVIDER_APPLE_MUSIC:
        if collection.format == Collection.FORMAT_ALBUM:
            return _refresh_collection_apple_music_album_data(collection, user)
        elif collection.format == Collection.FORMAT_PLAYLIST:
            return _refresh_collection_apple_music_playlist_data(collection, user)
    else:
        raise ValueError(
            f"Collection has bad provider: {collection.uuid}, {collection.provider}"
        )


def _refresh_track_spotify_data(track, user):
    Request = apps.get_model("networking", "Request")
    response = make_request(
        Request.TYPE_GET,
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
    Request = apps.get_model("networking", "Request")

    data = {
        "part": "snippet,contentDetails",
        "id": track.youtube_id,
        "key": settings.GOOGLE_API_KEY,
    }

    response = make_request(
        Request.TYPE_GET,
        "https://www.googleapis.com/youtube/v3/videos",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    response_json = response.json()

    # clean duration
    duration_raw = response_json["items"][0]["contentDetails"]["duration"]

    duration_ms = 0
    mode = None
    val = ""
    for char in duration_raw:
        if char in ["P", "T"]:
            continue

        if char in ["H", "M", "S"]:
            if char == "H":
                duration_ms += int(val) * 60 * 60 * 1000
            elif char == "M":
                duration_ms += int(val) * 60 * 1000
            elif char == "S":
                duration_ms += int(val) * 1000
            else:
                raise ValueError(f"Unexpected playtime character: {mode}")

            val = ""
            continue

        val += char

    # TODO refresh more data points
    track.duration_ms = duration_ms
    track.save()


def _refresh_collection_spotify_album_data(collection, user):
    Track = apps.get_model("music", "Track")
    CollectionListing = apps.get_model("music", "CollectionListing")
    Request = apps.get_model("networking", "Request")

    response = make_request(
        Request.TYPE_GET,
        f"https://api.spotify.com/v1/albums/{collection.spotify_id}/tracks",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()

    items = response_json["items"]
    data = []
    for item in items:
        artist_names = map(lambda o: o["name"], item["artists"])
        data.append(
            {
                # to be saved as Track instances
                "format": Track.FORMAT_TRACK,
                "provider": Track.PROVIDER_SPOTIFY,
                "external_id": item["uri"],
                "name": item["name"],
                "artist_name": ", ".join(artist_names),
                "album_name": collection.name,
                "duration_ms": int(item["duration_ms"]),
                "img_url": collection.img_url,
                # not saved in Track table
                "_disk_number": item["disc_number"],
                "_track_number": item["track_number"],
            }
        )

    # first sort by disk number, then by track number
    data = sorted(data, key=lambda d: (d["_disk_number"], d["_track_number"]))

    tracks = []
    track_eids = []
    for track_data in data:
        tracks.append(
            Track(
                format=track_data["format"],
                provider=track_data["provider"],
                external_id=track_data["external_id"],
                name=track_data["name"],
                artist_name=track_data["artist_name"],
                album_name=track_data["album_name"],
                img_url=track_data["img_url"],
                duration_ms=track_data["duration_ms"],
            )
        )
        track_eids.append(track_data["external_id"])

    # create Track objects if they do not already exist
    # TODO refresh more data points
    Track.objects.bulk_create(tracks, ignore_conflicts=True)
    track_qs = Track.objects.filter(external_id__in=track_eids)

    # wipe old CollectionListing objects
    # TODO this is not ok
    cl_by_tracks_qs = CollectionListing.objects.filter(
        track__external_id__in=track_eids
    )
    cl_by_collection_qs = CollectionListing.objects.filter(collection=collection)
    now = time_util.now()
    cl_by_tracks_qs.update(deleted_at=now)
    cl_by_collection_qs.update(deleted_at=now)

    # sort tracks by order one more time
    track_map = {}
    for track in track_qs:
        track_map[track.external_id] = track

    tracks = []
    for track_eid in track_eids:
        tracks.append(track_map[track_eid])

    # create CollectionListing objects if they do not already exist
    collection_listings = []
    for idx in range(len(tracks)):
        track = tracks[idx]
        collection_listings.append(
            CollectionListing(
                track=track,
                collection=collection,
                number=idx,
            )
        )
    CollectionListing.objects.bulk_create(collection_listings)


def _refresh_collection_spotify_playlist_data(collection, user):
    Track = apps.get_model("music", "Track")
    CollectionListing = apps.get_model("music", "CollectionListing")
    Request = apps.get_model("networking", "Request")

    response = make_request(
        Request.TYPE_GET,
        f"https://api.spotify.com/v1/playlists/{collection.spotify_id}",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()

    # items are pre-sorted here
    items = response_json["tracks"]["items"]
    data = []
    for item in items:
        artist_names = map(lambda o: o["name"], item["track"]["artists"])
        data.append(
            {
                "format": Track.FORMAT_TRACK,
                "provider": Track.PROVIDER_SPOTIFY,
                "external_id": item["track"]["uri"],
                "name": item["track"]["name"],
                "artist_name": ", ".join(artist_names),
                "album_name": collection.name,
                "duration_ms": item["track"]["duration_ms"],
                "img_url": item["track"]["album"]["images"][0]["url"],
            }
        )

    tracks = []
    track_eids = []
    for track_data in data:
        tracks.append(
            Track(
                format=track_data["format"],
                provider=track_data["provider"],
                external_id=track_data["external_id"],
                name=track_data["name"],
                artist_name=track_data["artist_name"],
                album_name=track_data["album_name"],
                img_url=track_data["img_url"],
                duration_ms=track_data["duration_ms"],
            )
        )
        track_eids.append(track_data["external_id"])

    # create Track objects if they do not already exist
    # TODO refresh more data points
    Track.objects.bulk_create(tracks, ignore_conflicts=True)
    track_qs = Track.objects.filter(external_id__in=track_eids)

    # wipe old CollectionListing objects to force refresh playlist
    # TODO this is not ok
    cl_by_tracks_qs = CollectionListing.objects.filter(
        track__external_id__in=track_eids
    )
    cl_by_collection_qs = CollectionListing.objects.filter(collection=collection)
    now = time_util.now()
    cl_by_tracks_qs.update(deleted_at=now)
    cl_by_collection_qs.update(deleted_at=now)

    # sort tracks by order one more time
    track_map = {}
    for track in track_qs:
        track_map[track.external_id] = track

    tracks = []
    for track_eid in track_eids:
        tracks.append(track_map[track_eid])

    # create CollectionListing objects if they do not already exist
    collection_listings = []
    for idx in range(len(tracks)):
        track = tracks[idx]
        collection_listings.append(
            CollectionListing(
                track=track,
                collection=collection,
                number=idx,
            )
        )
    CollectionListing.objects.bulk_create(collection_listings)


def _refresh_collection_apple_music_album_data(collection, user):
    CollectionListing = apps.get_model("music", "CollectionListing")
    Track = apps.get_model("music", "Track")
    Request = apps.get_model("networking", "Request")

    apple_music_token = generate_apple_music_token()
    apple_music_id = collection.external_id

    response = make_request(
        Request.TYPE_GET,
        f"https://api.music.apple.com/v1/catalog/us/albums/{apple_music_id}",
        headers={
            "Authorization": f"Bearer {apple_music_token}",
        },
    )
    response_json = response.json()

    items = response_json["data"][0]["relationships"]["tracks"]["data"]
    data = []
    for item in items:
        data.append(
            {
                # to be saved as Track instances
                "format": Track.FORMAT_TRACK,
                "provider": Track.PROVIDER_APPLE_MUSIC,
                "external_id": item["id"],
                "name": item["attributes"]["name"],
                "artist_name": item["attributes"]["artistName"],
                "album_name": item["attributes"]["albumName"],
                "duration_ms": item["attributes"]["durationInMillis"],
                "img_url": item["attributes"]["artwork"]["url"],
                # not saved in Track table
                "_disk_number": item["attributes"]["discNumber"],
                "_track_number": item["attributes"]["trackNumber"],
            }
        )

    # first sort by disk number, then by track number
    data = sorted(data, key=lambda d: (d["_disk_number"], d["_track_number"]))

    tracks = []
    track_eids = []
    for track_data in data:
        tracks.append(
            Track(
                format=track_data["format"],
                provider=track_data["provider"],
                external_id=track_data["external_id"],
                name=track_data["name"],
                artist_name=track_data["artist_name"],
                album_name=track_data["album_name"],
                img_url=track_data["img_url"],
                duration_ms=track_data["duration_ms"],
            )
        )
        track_eids.append(track_data["external_id"])

    # create Track objects if they do not already exist
    # TODO refresh more data points
    Track.objects.bulk_create(tracks, ignore_conflicts=True)
    track_qs = Track.objects.filter(external_id__in=track_eids)

    # wipe old CollectionListing objects
    # TODO this is not ok
    cl_by_tracks_qs = CollectionListing.objects.filter(
        track__external_id__in=track_eids
    )
    cl_by_collection_qs = CollectionListing.objects.filter(collection=collection)
    now = time_util.now()
    cl_by_tracks_qs.update(deleted_at=now)
    cl_by_collection_qs.update(deleted_at=now)

    # sort tracks by order one more time
    track_map = {}
    for track in track_qs:
        track_map[track.external_id] = track

    tracks = []
    for track_eid in track_eids:
        tracks.append(track_map[track_eid])

    # create CollectionListing objects if they do not already exist
    collection_listings = []
    for idx in range(len(tracks)):
        track = tracks[idx]
        collection_listings.append(
            CollectionListing(
                track=track,
                collection=collection,
                number=idx,
            )
        )
    CollectionListing.objects.bulk_create(collection_listings)


def _refresh_collection_apple_music_playlist_data(collection, user):
    CollectionListing = apps.get_model("music", "CollectionListing")
    Track = apps.get_model("music", "Track")
    Request = apps.get_model("networking", "Request")

    apple_music_token = generate_apple_music_token()
    apple_music_id = collection.external_id

    response = make_request(
        Request.TYPE_GET,
        f"https://api.music.apple.com/v1/catalog/us/playlists/{apple_music_id}",
        headers={
            "Authorization": f"Bearer {apple_music_token}",
        },
    )
    response_json = response.json()

    items = response_json["data"][0]["relationships"]["tracks"]["data"]
    data = []
    for item in items:
        data.append(
            {
                # to be saved as Track instances
                "format": Track.FORMAT_TRACK,
                "provider": Track.PROVIDER_APPLE_MUSIC,
                "external_id": item["id"],
                "name": item["attributes"]["name"],
                "artist_name": item["attributes"]["artistName"],
                "album_name": item["attributes"]["albumName"],
                "duration_ms": item["attributes"]["durationInMillis"],
                "img_url": item["attributes"]["artwork"]["url"],
                # not saved in Track table
                "_disk_number": item["attributes"]["discNumber"],
                "_track_number": item["attributes"]["trackNumber"],
            }
        )

    # first sort by disk number, then by track number
    data = sorted(data, key=lambda d: (d["_disk_number"], d["_track_number"]))

    tracks = []
    track_eids = []
    for track_data in data:
        tracks.append(
            Track(
                format=track_data["format"],
                provider=track_data["provider"],
                external_id=track_data["external_id"],
                name=track_data["name"],
                artist_name=track_data["artist_name"],
                album_name=track_data["album_name"],
                img_url=track_data["img_url"],
                duration_ms=track_data["duration_ms"],
            )
        )
        track_eids.append(track_data["external_id"])

    # create Track objects if they do not already exist
    # TODO refresh more data points
    Track.objects.bulk_create(tracks, ignore_conflicts=True)
    track_qs = Track.objects.filter(external_id__in=track_eids)

    # wipe old CollectionListing objects
    # TODO this is not ok
    cl_by_tracks_qs = CollectionListing.objects.filter(
        track__external_id__in=track_eids
    )
    cl_by_collection_qs = CollectionListing.objects.filter(collection=collection)
    now = time_util.now()
    cl_by_tracks_qs.update(deleted_at=now)
    cl_by_collection_qs.update(deleted_at=now)

    # sort tracks by order one more time
    track_map = {}
    for track in track_qs:
        track_map[track.external_id] = track

    tracks = []
    for track_eid in track_eids:
        tracks.append(track_map[track_eid])

    # create CollectionListing objects if they do not already exist
    collection_listings = []
    for idx in range(len(tracks)):
        track = tracks[idx]
        collection_listings.append(
            CollectionListing(
                track=track,
                collection=collection,
                number=idx,
            )
        )
    CollectionListing.objects.bulk_create(collection_listings)
