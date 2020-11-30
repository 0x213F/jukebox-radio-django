from jukebox_radio.music.models import GLOBAL_PROVIDER_JUKEBOX_RADIO, GLOBAL_PROVIDER_SPOTIFY, GLOBAL_PROVIDER_YOUTUBE

def get_search_results(user, provider_slug, query, formats):

    if provider_slug == GLOBAL_PROVIDER_JUKEBOX_RADIO:
        return _get_jukebox_radio_search_results(query, formats)

    if provider_slug == GLOBAL_PROVIDER_SPOTIFY:
        return _get_spotify_search_results(query, formats, user)

    if provider_slug == GLOBAL_PROVIDER_YOUTUBE:
        return _get_youtube_search_results(query, formats)

    raise ValueError(f'Unrecognized provider slug: {provider_slug}')


def _get_jukebox_radio_search_results(query, formats):
    pass

def _get_spotify_search_results(query, formats, user):
    pass

def _get_youtube_search_results(query, formats):
    pass
    params = {
        "part": "snippet",
        "q": query,
        "key": secrets.GOOGLE_API_KEY,
        "type": "video",
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

    response_data = []
    for item in response_json["items"]:
        youtube_id = item["id"]["videoId"]
        youtube_channel = item["snippet"]["channelTitle"]
        youtube_name = item["snippet"]["title"]
        youtube_img = item["snippet"]["thumbnails"]["high"]["url"]
        response_data.append(
            {
                "youtube_id": youtube_id,
                "record_artist": youtube_channel,
                "record_name": youtube_name,
                "record_thumbnail": youtube_img,
            }
        )

    return response_data
