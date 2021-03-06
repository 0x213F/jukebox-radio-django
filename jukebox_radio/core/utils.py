from datetime import timedelta
from urllib.parse import urlencode

import jwt
from django.conf import settings

from jukebox_radio.core.time import now


def generate_apple_music_token():
    alg = "ES256"
    time_now = now()
    time_expired = time_now + timedelta(hours=(24 * 7))

    headers = {
        "alg": alg,
        "kid": settings.APPLE_MUSIC_KEY_ID,
    }

    payload = {
        "iss": settings.APPLE_MUSIC_TEAM_ID,
        "exp": int(time_expired.strftime("%s")),
        "iat": int(time_now.strftime("%s")),
    }

    secret = settings.APPLE_MUSIC_AUTH_KEY_P8

    return jwt.encode(payload, secret, algorithm=alg, headers=headers)


def generate_redirect_uri(request):
    current_site = settings.SITE_URL
    endpoint = "spotify"
    return f"{current_site}{endpoint}"


def generate_spotify_authorization_uri(request):
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": generate_redirect_uri(request),
        "scope": ",".join(settings.SPOTIFY_USER_DATA_SCOPES),
    }
    query_str = urlencode(params)

    return f"https://accounts.spotify.com/authorize?{query_str}"


def generate_presigned_url(file):
    """
    Gets a file from an
    """
    if settings.APP_ENV == settings.APP_ENV_LOCAL:
        return "http://localhost:8000" + file.url

    if settings.APP_ENV != settings.APP_ENV_PROD:
        raise Exception("Unexpected enviornment")

    import boto3
    from botocore.client import Config

    FIVE_MINUTES = 60 * 5

    s3_client = boto3.client(
        "s3", config=Config(signature_version="s3v4"), region_name="us-west-1"
    )

    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": "jukebox-radio-prod",
            "Key": f"media/{file.name}",
        },
        ExpiresIn=FIVE_MINUTES,
    )
