def get_spotify_results(query, model, user):
    pass


def get_youtube_results(query, model):
    """"""
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
