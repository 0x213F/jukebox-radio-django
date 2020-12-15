import requests
from cryptography.fernet import Fernet

from django.apps import apps
from django.conf import settings
from django.db.models import Q

from jukebox_radio.music.const import GLOBAL_PROVIDER_JUKEBOX_RADIO
from jukebox_radio.music.const import GLOBAL_PROVIDER_SPOTIFY
from jukebox_radio.music.const import GLOBAL_PROVIDER_YOUTUBE
from jukebox_radio.networking.actions import make_request


def get_search_results(user, provider_slug, query, formats):
    Track = apps.get_model("music", "Track")
    Collection = apps.get_model("music", "Collection")

    if provider_slug == GLOBAL_PROVIDER_JUKEBOX_RADIO:
        search_results = _get_jukebox_radio_search_results(query, user)
    elif provider_slug == GLOBAL_PROVIDER_SPOTIFY:
        search_results = _get_spotify_search_results(query, formats, user)
    elif provider_slug == GLOBAL_PROVIDER_YOUTUBE:
        search_results = _get_youtube_search_results(query, formats)
    else:
        raise ValueError(f"Unrecognized provider slug: {provider_slug}")

    # - - - - - - - - - - - - - -
    # Save search results in DB
    tracks = []
    track_uuids = []
    track_eids = []
    collections = []
    collection_eids = []
    for search_result in search_results:

        # SKIP JUKEBOX RADIO
        if search_result["provider"] == GLOBAL_PROVIDER_JUKEBOX_RADIO:
            track_uuids.append(str(search_result["external_id"]))
            continue

        # TRACK
        if search_result["format"] in ["track", "video"]:
            tracks.append(
                Track(
                    format=search_result["format"],
                    provider=search_result["provider"],
                    external_id=search_result["external_id"],
                    name=search_result["name"],
                    artist_name=search_result["artist_name"],
                    album_name=search_result["album_name"],
                    img_url=search_result["img_url"],
                )
            )
            track_eids.append(search_result["external_id"])

        # COLLECTION
        else:
            collections.append(
                Collection(
                    format=search_result["format"],
                    provider=search_result["provider"],
                    external_id=search_result["external_id"],
                    name=search_result["name"],
                    artist_name=search_result["artist_name"],
                    img_url=search_result["img_url"],
                )
            )
            collection_eids.append(search_result["external_id"])

    Track.objects.bulk_create(tracks, ignore_conflicts=True)
    Collection.objects.bulk_create(collections, ignore_conflicts=True)

    # - - - - - - - - - - - - - -
    # Return relevant DB objects
    track_qs = Track.objects.filter(
        Q(uuid__in=track_uuids) | Q(external_id__in=track_eids)
    )
    collection_qs = Collection.objects.filter(external_id__in=collection_eids)
    db_objs = []
    for obj_qs in [track_qs, collection_qs]:
        for obj in obj_qs:
            db_objs.append(
                {
                    "class": obj.__class__.__name__,
                    "uuid": getattr(obj, "uuid"),
                    "format": getattr(obj, "format"),
                    "provider": getattr(obj, "provider"),
                    "external_id": getattr(obj, "external_id"),
                    "name": getattr(obj, "name"),
                    "artist_name": getattr(obj, "artist_name"),
                    "img_url": getattr(obj, "img_url"),
                }
            )

    return db_objs


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Jukebox Radio


def _get_jukebox_radio_search_results(query, user):
    Track = apps.get_model("music", "Track")

    track_qs = Track.objects.filter(
        Q(
            user=user,
            provider=Track.PROVIDER_JUKEBOX_RADIO,
            artist_name__icontains=query,
        )
        | Q(
            user=user,
            provider=Track.PROVIDER_JUKEBOX_RADIO,
            album_name__icontains=query,
        )
        | Q(user=user, provider=Track.PROVIDER_JUKEBOX_RADIO, name__icontains=query)
    )

    tracks = []
    for track in track_qs:
        tracks.append(
            {
                "format": Track.FORMAT_TRACK,
                "provider": Track.PROVIDER_JUKEBOX_RADIO,
                "external_id": track.uuid,
                "name": track.name,
                "artist_name": track.artist_name,
                "album_name": track.album_name,
                "img_url": track.img.url,
            }
        )

    return tracks


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Spotify


def _get_spotify_search_results(query, formats, user):
    Collection = apps.get_model("music", "Collection")
    Track = apps.get_model("music", "Track")
    Request = apps.get_model("networking", "Request")

    formats = set(formats).intersection(
        set([Track.FORMAT_TRACK, Collection.FORMAT_ALBUM, Collection.FORMAT_PLAYLIST])
    )

    data = {
        "q": query,
        "type": ",".join(formats),
    }

    spotify_access_token = user.spotify_access_token

    response = make_request(
        Request.TYPE_GET,
        "https://api.spotify.com/v1/search",
        data=data,
        headers={
            "Authorization": f"Bearer {spotify_access_token}",
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()

    data = []

    # - - - - - - - - - - - - -
    # Glue everything together
    if "albums" in response_json:
        items = response_json["albums"]["items"]
        for item in items:
            data.append(
                {
                    "format": "album",
                    "provider": "spotify",
                    "external_id": item["uri"],
                    "name": item["name"],
                    "artist_name": ", ".join([a["name"] for a in item["artists"]]),
                    "img_url": item["images"][0]["url"],
                }
            )
    if "playlists" in response_json:
        items = response_json["playlists"]["items"]
        for item in items:
            data.append(
                {
                    "format": "playlist",
                    "provider": "spotify",
                    "external_id": item["uri"],
                    "name": item["name"],
                    "artist_name": item["owner"]["display_name"],
                    "img_url": item["images"][0]["url"],
                }
            )
    if "tracks" in response_json:
        items = response_json["tracks"]["items"]
        for item in items:
            data.append(
                {
                    "format": "track",
                    "provider": "spotify",
                    "external_id": item["uri"],
                    "name": item["name"],
                    "artist_name": ", ".join([a["name"] for a in item["artists"]]),
                    "album_name": item["album"]["name"],
                    "img_url": item["album"]["images"][0]["url"],
                }
            )

    return data


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# YouTube

YOUTUBE_KIND_PLAYLIST = "youtube#playlist"
YOUTUBE_KIND_VIDEO = "youtube#video"


def _get_youtube_search_results(query, formats):
    """
    Get YouTube search results
    """
    Track = apps.get_model("music", "Track")
    Request = apps.get_model("networking", "Request")

    formats = set(formats).intersection(set([Track.FORMAT_VIDEO]))

    if not formats:
        return []

    data = {
        "part": "snippet",
        "q": query,
        "key": settings.GOOGLE_API_KEY,
        "type": ",".join(formats),
        "videoEmbeddable": True,
        "maxResults": 25,
    }

    response = make_request(
        Request.TYPE_GET,
        "https://www.googleapis.com/youtube/v3/search",
        data=data,
        headers={
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()

    cleaned_data = []
    if "items" not in response_json:
        return cleaned_data

    for item in response_json["items"]:

        youtube_id = item["id"]["videoId"]
        youtube_channel_name = item["snippet"]["channelTitle"]
        youtube_video_name = item["snippet"]["title"]
        youtube_img_lg = item["snippet"]["thumbnails"]["high"]["url"]

        cleaned_data.append(
            {
                "format": Track.FORMAT_VIDEO,
                "provider": GLOBAL_PROVIDER_YOUTUBE,
                "external_id": youtube_id,
                "name": youtube_video_name,
                "artist_name": youtube_channel_name,
                "album_name": "",  # TODO maybe this shouldn't just be an empty string
                "img_url": youtube_img_lg,
            }
        )

    return cleaned_data
