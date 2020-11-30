import requests

from django.apps import apps
from django.conf import settings

from jukebox_radio.music.models import GLOBAL_PROVIDER_JUKEBOX_RADIO, GLOBAL_PROVIDER_SPOTIFY, GLOBAL_PROVIDER_YOUTUBE

def get_search_results(user, provider_slug, query, formats):
    Track = apps.get_model("music", "Track")
    Collection = apps.get_model("music", "Collection")

    if provider_slug == GLOBAL_PROVIDER_JUKEBOX_RADIO:
        search_results = _get_jukebox_radio_search_results(query, formats)
    elif provider_slug == GLOBAL_PROVIDER_SPOTIFY:
        search_results = _get_spotify_search_results(query, formats, user)
    elif provider_slug == GLOBAL_PROVIDER_YOUTUBE:
        search_results = _get_youtube_search_results(query, formats)
    else:
        raise ValueError(f'Unrecognized provider slug: {provider_slug}')

    # # # # # # # # # # # # # # #
    # Save search results in DB
    tracks = []
    track_eids = []
    collections = []
    collection_eids = []
    for search_result in search_results:

        # TRACK
        if search_result['format'] in ['track', 'video']:
            tracks.append(
                Track(
                    format=search_result["format"],
                    provider=search_result["provider"],
                    external_id=search_result["external_id"],
                    name=search_result["name"],
                    artist_name=search_result["artist_name"],
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

    # # # # # # # # # # # # # # #
    # Return relevant DB objects
    track_qs = Track.objects.filter(external_id__in=track_eids)
    collection_qs = Collection.objects.filter(external_id__in=collection_eids)

    return search_results

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Jukebox Radio

def _get_jukebox_radio_search_results(query, formats):
    pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Spotify

def _get_spotify_search_results(query, formats, user):
    pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# YouTube

YOUTUBE_KIND_PLAYLIST = "youtube#playlist"
YOUTUBE_KIND_VIDEO = "youtube#video"

def _get_youtube_search_results(query, formats):
    '''
    Get YouTube search results
    '''
    Track = apps.get_model('music', 'Track')

    try:
        assert set(formats) == set([Track.FORMAT_VIDEO])
    except AssertionError:
        raise ValueError(f'Invalid formats: {formats}')

    params = {
        "part": "contentDetails",
        "q": query,
        "key": settings.GOOGLE_API_KEY,
        "type": 'video',
        "videoEmbeddable": True,
        "maxResults": 16,
    }

    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params=params,
        headers={
            "Content-Type": "application/json",
        },
    )
    response_json = response.json()
    print(response_json)

    cleaned_data = []
    if 'items' not in response_json:
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
                "img_url": youtube_img_lg,
            }
        )

    return cleaned_data
